#!/usr/bin/python

#    This file is part of Morse.
#
#    Morse is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Morse is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Morse.  If not, see <http://www.gnu.org/licenses/>.

import re
from . import app
from enum import GROUP_ID_REGISTERED
from mixins import GuestMixin
from models import db, User, UserWebsite, Board, Group, GroupMember, GroupMode 
from models import Topic, get_my_boards
from wrappers import PostWrapper, TopicWrapper
from rights import admin_rights_required, check_ban, possibly_banned 
from flask import render_template, url_for, request, redirect
from flask.ext.login import LoginManager, login_user 
from flask.ext.login import logout_user, login_required 
from flask.ext.login import current_user

""" This module contains all views of morse """

# Integration into flask login extension
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.anonymous_user = GuestMixin

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

@app.route('/install')
def install ():
    """ 
    Creates base tables / installs default config
    :rtype: html
    """
    db.create_all()
    
    # !important: dont't change the order
    gadmin = Group("Administrators", True, True, True, True, 4)
    gmods = Group("Moderators", False, True, True, True, 3)
    gregistered = Group("Registered", False, False, False, False, 2)
    gguests = Group("Guests", False, False, False, False, 1)
    
    db.session.add(gadmin)
    db.session.add(gmods)
    db.session.add(gregistered)
    db.session.add(gguests)

    admin = User("admin", "admin", "root@localhost")
    db.session.add(admin)
    db.session.commit()

    rel = GroupMember(admin.id,gadmin.id)
    mode1 = GroupMode(0, gadmin.id, True, True, True) 
    mode2 = GroupMode(0, gmods.id, True, True, True) 
    mode3 = GroupMode(0, gregistered.id, True, True, True) 
    mode4 = GroupMode(0, gguests.id, True, False, True) 

    db.session.add(rel)
    db.session.add(mode1)
    db.session.add(mode2)
    db.session.add(mode3)
    db.session.add(mode4)

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/account/register' , methods=['GET','POST'])
def register():
    """ 
    Renders the register view on GET / registers a new user on POST
    :rtype: html
    """
    if request.method == 'GET':
        return render_template('account/register.html')
    
    username = request.form['username']
    password = request.form['password']
    email    = request.form['email']

    # TODO: mail authentication check

    # make sure, that username doesn't exist
    # in the database (we allow multiple accounts
    # for one email)
    user_exists = User.query.filter(User.username == username).first()
    if user_exists:
        return render_template('account/register.html', alert = 'userexists');

    pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
    match = re.search(pattern, email)
    if not match:
        return render_template('account/register.html', alert = 'invalidemail');

    # all fine, create the new user
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()

    # insert the user in the registered group
    relationship = GroupMember(user.id, GROUP_ID_REGISTERED)
    db.session.add(relationship)
    db.session.commit()

    login_user(user)

    return render_template('account/redirect.html', alert = 'registered')

 
@app.route('/account/login',methods=['GET','POST'])
def login():
    """ 
    Renders the login view on GET / logs a user in on POST
    :rtype: html
    """
    if request.method == 'GET':
        return render_template('account/login.html')

    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter(User.username == username).first()

    if not registered_user or not registered_user.has_password(password):
        return render_template('account/login.html', alert = 'loginfailed')

    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/account/logout')
def logout():
    """ 
    Logs out and redirects to index
    :rtype: html
    """
    logout_user()
    return redirect(url_for('index')) 

@app.route('/')
@possibly_banned
def index():
    """ 
    Renders the index view
    :rtype: html
    """
    check_ban()
    visible, readable, writable = get_my_boards()
    return render_template('index.html', boards = visible)

@app.route('/board/<board_str>')
@possibly_banned
def board(board_str):
    """ 
    Renders the board view for board_id
    :rtype: html
    """
    board_id = int(board_str.split("-")[0])

    check_ban(board_id)

    # TODO: order topics by timestamp
    visible, readable, writable = get_my_boards( get_only_ids = True)

    # i decided not to do a seperate check, if the board
    # exists (and return a 404 if not) in order leak as
    # few information as possible to an attacker.
    if not int(board_id) in readable:
        return render_template('4xx/403-default.html'), 403

    board  = Board.query.filter(Board.id == board_id).first()
    topics = Topic.query.filter(Topic.board_id == board_id).all()
    topics = map(TopicWrapper, topics)
    return render_template('board.html', board = board, topics = topics)

@app.route('/admin')
@login_required
@admin_rights_required
def admin():
    """ 
    Renders the admin view
    :rtype: html
    """
    return render_template('admin.html')

def formlist_to_group_ids (form, prefix):
    i = 0
    group_ids = []
    while True:
        try:
            group_id = form[prefix + str(i)]
            group_ids.append(group_id)
            i += 1
        except KeyError:
            break
    return group_ids

def GroupModes (board_id, group_ids, r, w, v):
    """ A GroupMode factory, that allows creating
    a list of GroupModes at once """
    groupmodes = []
    for group_id in group_ids:
        groupmode = GroupMode(board_id, group_id, r, w, v)
        groupmodes.append(groupmode)
    return groupmodes

def add_to_session (objectlist):
    """ adds a LIST of objects to session """
    for o in objectlist:
        db.session.add(o)

def DummyBoard ():
    """ Generates a Board with Id 0 """
    board = Board()
    board.id = 0
    return board

@app.route('/admin/newboard', methods=["GET", "POST"])
@login_required
@admin_rights_required
def newboard():
    """ 
    Renders the new board view
    (and does the backend logic)
    :rtype: html
    """
    if request.method == 'GET':
        dummy = DummyBoard()
        return render_template('admin/newboard.html', board = dummy)

    title = request.form['boardtitle']
    description = request.form['boardescription']
    board = Board(title, description)
    db.session.add(board)
    db.session.commit()

    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    knowonly_ids = formlist_to_group_ids(request.form, "knowonly")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    # please note: GroupMode() != GroupModes()
    ignorant_modes = GroupModes(board.id, ignorant_ids, False, False, False)
    knowonly_modes = GroupModes(board.id, knowonly_ids, False, False, True)
    readonly_modes = GroupModes(board.id, readonly_ids, True, False, True)
    poster_modes   = GroupModes(board.id, poster_ids, True, True, True)

    add_to_session(ignorant_modes)
    add_to_session(knowonly_modes)
    add_to_session(readonly_modes)
    add_to_session(poster_modes)

    db.session.commit()

    return redirect(url_for('index'))

def update_groupmodes (board_id, group_ids, r, w, v):
    """ updates a list of groupmodes identified by board id
    and group ids """
    for group_id in group_ids:
        groupmode = GroupMode.query.filter(GroupMode.board_id == board_id,\
                                           GroupMode.group_id == group_id).first()
        if not groupmode:
            continue

        groupmode.r = r
        groupmode.w = w
        groupmode.v = v

@app.route('/admin/updateboard/<board_id>', methods=["GET", "POST"])
@login_required
@admin_rights_required
def updateboard(board_id):
    """ 
    Renders the update board view
    (and does the backend logic)
    :rtype: html
    """
    board = Board.query.get(board_id)
    if not board:
        return "", 400

    if request.method == 'GET':
        return render_template('admin/updateboard.html', board = board)

    board.title = request.form['boardtitle']
    board.description = request.form['boardescription']

    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    knowonly_ids = formlist_to_group_ids(request.form, "knowonly")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    update_groupmodes(board.id, ignorant_ids, False, False, False)
    update_groupmodes(board.id, knowonly_ids, False, False, True)
    update_groupmodes(board.id, readonly_ids, True, False, True)
    update_groupmodes(board.id, poster_ids, True, True, True)

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/admin/groups', methods=['GET'])
@login_required
@admin_rights_required
def manage_groups ():
    """ 
    Renders the group management view
    :rtype: html
    """
    groups = Group.query.all()
    return render_template('admin/groups.html', groups = groups)

def hyperlink (website):
    """ mapping function (see below) """
    return website.hyperlink

@app.route('/account/settings')
@login_required
@possibly_banned
def settings():
    """ 
    Renders the settings view
    :rtype: html
    """
    check_ban()

    websites = UserWebsite.query.filter(UserWebsite.user_id == current_user.id).all()
    if not websites:
        websites = [""]
    else:
        websites = map(hyperlink, websites)

    bio = current_user.bio
    email = current_user.email

    return render_template('account/settings.html', \
                            websites = websites, bio = bio, email = email)


@app.route('/topic/<topic_str>', methods=['GET'])
@possibly_banned
def showtopic (topic_str):
    """ 
    renders topic view
    :param topic_id: indicates topic view to render
    :rtype: html 
    """
    topic_id = int(topic_str.split("-")[0])
    # TODO: page numbers
    # TODO: order by timestamp
    topic = Topic.query.get(topic_id)
    if not topic:
       return "nosuchtopic", 400

    check_ban(topic.board_id)

    topic = TopicWrapper(topic)
    visible, readable, writable = get_my_boards( get_only_ids = True)
    if not topic.board_id in readable:
        return render_template('4xx/403-default.html'), 403

    posts = map(PostWrapper, topic.posts)
    return render_template("topic.html", topic = topic, posts = posts)

