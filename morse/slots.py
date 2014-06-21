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
from models import db, User, UserWebsite, Board, Group, GroupMember, GroupMode 
from models import Post, Topic, get_my_boards
from wrappers import PostWrapper, TopicWrapper
from rights import admin_rights_required, certain_rights_required, check_ban, possibly_banned 
from protocols import ajax_triggered
from flask import request, jsonify
from flask.ext.login import LoginManager
from flask.ext.login import login_required 
from flask.ext.login import current_user

""" this module contains all the ajax slots """

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
    if not topic:
        return "notfound", 404

    topic.closed = True
    db.session.commit()
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
    if not topic:
        return "notfound", 404

    topic.closed = False
    db.session.commit()
    return jsonify(openedID=topic_id)

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
    already_in_group = GroupMember.query.filter(GroupMember.user_id == user_id,
                                                GroupMember.group_id == group_id).first()
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
    rel = GroupMember.query.filter(GroupMember.user_id == user_id,
                                   GroupMember.group_id == group_id).first()
    if not rel:
        return "notingroup", 400

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
    already_exists = Group.query.filter(Group.name == name).first()
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
    group = Group.query.get(group_id)
    if not group:
       return "nosuchgroup", 400

    members = GroupMember.query.filter(GroupMember.group_id == group_id).all()
    for m in members:
        db.session.delete(m)

    modes = GroupMode.query.filter(GroupMode.group_id == group_id).all()
    for m in modes:
        db.session.delete(m)

    db.session.delete(group)

    db.session.commit()
    return ""

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

    websites = UserWebsite.query.filter(UserWebsite.user_id == current_user.id).all()
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
    topic = Topic.query.get(topic_id)
    if not topic:
       return "nosuchtopic", 400

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
        post = Post.query.get(post_id)
        if not post:
            continue
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
    topic_id = int(request.json)
    topic = Topic.query.get(topic_id)
    if not topic:
        return "nosuchtopic", 400
 
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
    topic_id = int(request.json)
    topic = Topic.query.get(topic_id)
    if not topic:
        return "nosuchtopic", 400

    topic = TopicWrapper(topic)
    topic.unfollow()
    return ""
