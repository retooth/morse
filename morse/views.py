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

from . import app
from enum import GROUP_ID_REGISTERED
from mixins import GuestMixin
from models import db, User, UserWebsite, Board, Group, GroupMember, GroupMode 
from models import Post, Topic, TopicFollow, PostRead, get_my_boards
from models import LimitedIPBan, PermaIPBan, LimitedUserBan, PermaUserBan
from wrappers import PostWrapper, TopicWrapper
from rights import admin_rights_required, certain_rights_required, check_ban, possibly_banned 
from protocols import ajax_triggered
from flask import render_template, url_for, request, g, jsonify, redirect
from flask.ext.login import LoginManager, login_user 
from flask.ext.login import logout_user, login_required 
from flask.ext.login import current_user

""" This module contains all views of morse """

# group modes save the default state
# with this dummy board id. default state
# is shown when creating a new board
DEFAULT_MODE_DUMMY_ID = 0

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
    user_exists = User.query.filter(User.username.like(username)).first()
    if user_exists:
        return render_template('account/register.html', alert = 'userexists');

    # all fine, create the new user
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()

    # insert the user in the registered group
    relationship = GroupMember(user.id, GROUP_ID_REGISTERED)
    db.session.add(relationship)
    db.session.commit()

    login_user(user)

    # FIXME: redirect instead of render (bad req bug) - howto pass alert?
    return render_template('boards.html', alert = 'registered')

 
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
    registered_user = User.query.filter(User.username.like(username)).first()

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

@app.route('/board/<board_id>')
@possibly_banned
def board(board_id):
    """ 
    Renders the board view for board_id
    :rtype: html
    """
    check_ban(board_id)

    # TODO: order topics by timestamp
    visible, readable, writable = get_my_boards( get_only_ids = True)
    if not int(board_id) in readable:
        return render_template('4xx/403-default.html'), 403

    board  = Board.query.filter(Board.id.like(board_id)).first()
    topics = Topic.query.filter(Topic.board_id.like(board_id)).all()
    topics = map(TopicWrapper, topics)
    return render_template('board.html', board = board, topics = topics)

@app.route('/closethread', methods=['POST'])
@login_required
@certain_rights_required(may_close=True)
@ajax_triggered
def closethread ():
    """ 
    closes a thread defined by topicID in ajax request. 
    this function is called by the javascript event handler 
    for .closethread in main.js
    """
    # XXX: check for bans? should moderators be bannable?
    topic_id = request.json['topicID']
    topic = Topic.query.get(topic_id)
    # FIXME (global) always check if ids were found
    topic.closed = True
    db.session.commit()
    #XXX see return of openthread
    return jsonify(closedID=topic_id)

@app.route('/openthread', methods=['POST'])
@login_required
@certain_rights_required(may_close=True)
@ajax_triggered
def openthread ():
    """ 
    closes a thread defined by topicID in ajax request. 
    this function is called by the javascript event handler 
    for .openthread in main.js
    """
    # XXX: check for bans? should moderators be bannable?
    topic_id = request.json['topicID']
    topic = Topic.query.get(topic_id)
    topic.closed = False
    db.session.commit()
    # XXX: this seems to be the only solution
    # for the ajax callback to know which button
    # was pressed. however it seems strange and
    # unclean to me. maybe i'm just missing
    # something...
    return jsonify(openedID=topic_id)

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
    ignorant_modes = GroupModes(board.id, ignorant_ids, 0, 0, 0)
    knowonly_modes = GroupModes(board.id, knowonly_ids, 0, 0, 1)
    readonly_modes = GroupModes(board.id, readonly_ids, 1, 0, 1)
    poster_modes   = GroupModes(board.id, poster_ids, 1, 1, 1)

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
        groupmode = GroupMode.query.filter(GroupMode.board_id.like(board_id),\
                                           GroupMode.group_id.like(group_id)).first()
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

    update_groupmodes(board.id, ignorant_ids, 0, 0, 0)
    update_groupmodes(board.id, knowonly_ids, 0, 0, 1)
    update_groupmodes(board.id, readonly_ids, 1, 0, 1)
    update_groupmodes(board.id, poster_ids, 1, 1, 1)

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

@app.route('/userlist.json', methods=['GET'])
@login_required
@admin_rights_required
@ajax_triggered
def get_users ():
    """ 
    Gets a list of users matching GET 
    parameter pattern.
    :rtype: json
    """
    pattern = request.args.get('pattern')
    if pattern:
        users = User.query.filter(User.username.ilike('%' + pattern + '%'))
    else:
        users = User.query.all()

    userlist = []
    for u in users:
        userlist.append([u.id, u.username])

    return jsonify(users = userlist)    

@app.route('/groups/adduser', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def add_user_to_group():
    """
    Adds new user to a group.
    """
    user_id = request.json["userID"]
    group_id = request.json["groupID"]
    # check if user is already in group
    already_in_group = GroupMember.query.filter(GroupMember.user_id.like(user_id),
                                                GroupMember.group_id.like(group_id)).first()
    if already_in_group:
        return "alreadyingroup", 412

    rel = GroupMember(user_id, group_id)
    db.session.add(rel)
    db.session.commit()

    return ""

@app.route('/groups/removeuser', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def remove_user_from_group():
    """
    Removes a user from a group.
    """
    user_id = request.json["userID"]
    group_id = request.json["groupID"]
    # check if user is already in group
    rel = GroupMember.query.filter(GroupMember.user_id.like(user_id),
                                   GroupMember.group_id.like(group_id)).first()
    if not rel:
        return "notingroup", 404

    db.session.delete(rel)
    db.session.commit()

    return ""

@app.route('/groups/changelabel', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def change_group_label():
    """
    changes the label of a group.
    """
    group_id = request.json["groupID"]
    label_id = request.json["labelID"]
    # check if user is already in group
    group = Group.query.get(group_id)
    if not group:
        return "groupnotfound", 404

    group.label = label_id
    db.session.commit()

    return ""

@app.route('/groups/updateflags', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def update_group_flags ():
    """ 
    updates the group flags defined by groupID. (label type and
    group flags) this function is called by the javascript 
    event handler for #updategroups in main.js.
    """
    group_id = request.json["groupID"]
    group = Group.query.get(group_id)
    if not group:
        return "groupnotfound", 404

    group.may_edit = request.json["mayEdit"]
    group.may_close = request.json["mayClose"]
    group.may_stick = request.json["mayStick"]
    db.session.commit()

    return ""

@app.route('/groups/create', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def create_group ():
    """ 
    creates a new group and returns its id as json
    this function is called by the javascript 
    event handler for #newgroupname in main.js.
    """
    name = request.json['name']

    #check if group already exists
    already_exists = Group.query.filter(Group.name.like(name)).first()
    if already_exists:
        return "groupexists", 412

    group = Group(name)
    db.session.add(group)
    db.session.commit()

    boards = Board.query.all()
    for board in boards:
        mode = GroupMode(board.id, group.id)
        db.session.add(mode)

    mode_default = GroupMode(DEFAULT_MODE_DUMMY_ID, group.id)
    db.session.add(mode_default)

    db.session.commit()

    return jsonify(newGroupID = group.id, name = name)

@app.route('/groups/delete', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def delete_group ():
    """ 
    deletes a group and all its dependencies
    this function is called by the javascript 
    event handler for .deletegroup in main.js.
    """
    group_id = request.json['groupID']

    members = GroupMember.query.filter(GroupMember.group_id.like(group_id)).all()
    for m in members:
        db.session.delete(m)

    modes = GroupMode.query.filter(GroupMode.group_id.like(group_id)).all()
    for m in modes:
        db.session.delete(m)

    group = Group.query.get(group_id)
    db.session.delete(group)

    db.session.commit()
    return ""

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

    websites = UserWebsite.query.filter(UserWebsite.user_id.like(current_user.id)).all()
    if not websites:
        websites = [""]
    else:
        websites = map(hyperlink, websites)

    bio = current_user.bio
    email = current_user.email

    return render_template('account/settings.html', \
                            websites = websites, bio = bio, email = email)

@app.route('/account/updateinfo', methods=['POST'])
@login_required
@possibly_banned
@ajax_triggered
def updateinfo ():
    """
    Updates bio/websites of user. Is called by the javascript
    event callback of #updateinfo
    """
    check_ban()

    info = request.json
    user = User.query.get(current_user.id)
    user.bio = info["bio"]

    websites = UserWebsite.query.filter(UserWebsite.user_id.like(current_user.id)).all()
    # it's easier to remove and redo them
    # than to check which has changed and
    # which is new
    for website in websites:
        db.session.delete(website)

    # commit early, so ids are free again
    db.session.commit()

    for website in info["websites"]:
        w = UserWebsite(current_user, website)
        db.session.add(w)

    db.session.commit()
    return ""

@app.route('/account/update', methods=['POST'])
@login_required
@possibly_banned
@ajax_triggered
def updateaccount ():
    """
    Updates email/password of user. Is called by the javascript
    event callback of #updateaccount
    """
    check_ban()

    oldpassword = request.json["oldpassword"]
    if not current_user.has_password(oldpassword):
        return "wrongpassword", 403

    newpassword = request.json["newpassword"]
    if newpassword:
        current_user.password = newpassword

    current_user.email = request.json["newemail"]
    db.session.commit()
    return ""

@app.route('/board/<int:board_id>/starttopic', methods=['POST'])
@possibly_banned
@ajax_triggered
def starttopic (board_id):
    """ 
    Creates a new topic. Is called by the javascript event
    callback for #docreate
    :param board_id: board in which the new topic 
                     should be started
    :rtype: json 
    """
    check_ban(board_id)

    visible, readable, writable = get_my_boards( get_only_ids = True )
    if not board_id in writable:
        return "forbidden", 403 

    title = request.json["title"]
    text = request.json["text"]

    topic = Topic(board_id, title)
    db.session.add(topic)
    db.session.commit()

    wrapper = TopicWrapper(topic)
    wrapper.follow()

    post = Post(current_user.id, text, topic.id, request.remote_addr)
    db.session.add(post)
    db.session.commit()
    post = PostWrapper(post)
    post.read()

    return jsonify(topicId=topic.id)


@app.route('/topic/<topic_id>/post', methods=['POST'])
@possibly_banned
@ajax_triggered
def post (topic_id):
    """ 
    Creates a new post. Is called by the javascript event
    callback for #dopost
    :param topic_id: topic to which the posts belongs
    :rtype: json 
    """
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    check_ban(topic.board_id)

    visible, readable, writable = get_my_boards(get_only_ids = True)
    if not topic.board_id in writable:
        return "forbidden", 403

    if topic.closed:
        return "forbidden", 403

    if not current_user.is_anonymous(): 
        wrapper = TopicWrapper(topic)
        wrapper.follow()

    text = request.json["text"]
    post = Post(current_user.id, text, topic_id, request.remote_addr)
    db.session.add(post)
    db.session.commit()
    post = PostWrapper(post)
    post.read()

    return jsonify(postId = post.id)


@app.route('/topic/<topic_id>', methods=['GET'])
@possibly_banned
def showtopic (topic_id):
    """ 
    renders topic view
    :param topic_id: indicates topic view to render
    :rtype: html 
    """

    # TODO: page numbers
    # TODO: order by timestamp
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    check_ban(topic.board_id)

    topic = TopicWrapper(topic)
    visible, readable, writable = get_my_boards( get_only_ids = True)
    if not topic.board_id in readable:
        return render_template('4xx/403-default.html'), 403

    posts = map(PostWrapper, topic.posts)
    return render_template("topic.html", topic = topic, posts = posts)

@app.route('/read', methods=['POST'])
@ajax_triggered
def read ():
    """ 
    marks posts as read. this function is called via ajax
    by the javascript function readVisiblePosts in main.js
    """
    # just return success and do nothing
    # if user is guest
    if current_user.is_anonymous():
        return ""
    
    post_ids = request.json
    posts = []
    for post_id in post_ids:
        post = Post.query.filter(Post.id.like(post_id)).first()
        posts.append(post)
    posts = map(PostWrapper, posts)
    for post in posts:
        post.read()
    return ""

@app.route('/follow', methods=['POST'])
@login_required
@ajax_triggered
def follow ():
    """ 
    follows a topic. this function is called via ajax
    by the click event handler for #followswitch in main.js
    """
    topic_id = request.json
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    topic = TopicWrapper(topic)
    topic.follow()
    return ""

@app.route('/unfollow', methods=['POST'])
@login_required
@ajax_triggered
def unfollow ():
    """ 
    unfollows a topic. this function is called via ajax
    by the click event handler for #followswitch in main.js
    """
    topic_id = request.json
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    topic = TopicWrapper(topic)
    topic.unfollow()
    return ""
