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
from flask.ext.login import login_required, current_user
from flask import jsonify, request
from ..rights import certain_rights_required, check_ban, possibly_banned
from ..protocols import ajax_triggered
from ..models import db
from ..models.core import Board
from ..models.discussion import Topic, Post, PostRead
from ..wrappers import TopicWrapper, PostWrapper
from ..mappers import to_id, to_post_id
from lists import PostList
from sqlalchemy import not_

@app.route('/topic/<topic_str>/post', methods=['POST'])
@possibly_banned
@ajax_triggered
def post (topic_str):
    """ 
    Creates a new post. Is called by the javascript event
    callback for #dopost
    :param topic_id: topic to which the posts belongs
    :rtype: json 
    """
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
       return "nosuchtopic", 400

    check_ban(topic.board_id)

    topic = TopicWrapper(topic)
    if not current_user.may_post_in(topic.board):    
        return "forbidden", 403

    if topic.closed:
        return "forbidden", 403

    if not current_user.is_anonymous(): 
        topic.follow()

    text = request.json["text"]
    post = Post(current_user.id, text, topic_id, request.remote_addr)
    
    has_posted_at_least_once = Post.query.filter(Post.topic_id == topic_id, Post.user_id == current_user.id).first()
    if not has_posted_at_least_once:
        topic.poster_count += 1

    topic.post_count += 1
    #TODO: calculate interesting

    db.session.add(post)
    db.session.commit()

    post = PostWrapper(post)
    post.read()

    return jsonify(postId = post.id)

@app.route('/topic/<topic_str>/close', methods=['POST'])
@login_required
@certain_rights_required(may_close=True)
@ajax_triggered
def close_topic (topic_str):
    """ 
    closes a topic.
    this function is called by the javascript event handler 
    for .close-topic in board.js as well as by the event
    handler for #close-topic in topic.js
    """
    topic_id = int(topic_str.split("-")[0])

    # XXX: check for bans? should moderators be bannable?
    topic = Topic.query.get(topic_id)
    if not topic:
        return "notfound", 404

    topic.closed = True
    db.session.commit()
    return jsonify(closedID=topic_id)

@app.route('/topic/<topic_str>/reopen', methods=['POST'])
@login_required
@certain_rights_required(may_close=True)
@ajax_triggered
def reopen_topic (topic_str):
    """ 
    reopens a topic.
    this function is called by the javascript event handler 
    for .reopen-topic in board.js as well as by the event
    handler for #reopen-topic in topic.js
    """
    # XXX: check for bans? should moderators be bannable?
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
        return "notfound", 404

    topic.closed = False
    db.session.commit()
    return jsonify(openedID=topic_id)

@app.route('/topic/<topic_str>/follow', methods=['POST'])
@login_required
@ajax_triggered
def follow (topic_str):
    """ 
    follows a topic. this function is called via ajax
    by the click event handler for #follow-topic-switch in topic.js
    """
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
        return "nosuchtopic", 400
 
    topic = TopicWrapper(topic)
    topic.follow()
    return ""

@app.route('/topic/<topic_str>/unfollow', methods=['POST'])
@login_required
@ajax_triggered
def unfollow (topic_str):
    """ 
    unfollows a topic. this function is called via ajax
    by the click event handler for #follow-topic-switch in topic.js
    """
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
        return "nosuchtopic", 400

    topic = TopicWrapper(topic)
    topic.unfollow()
    return ""

@app.route('/topic/<topic_str>/posts.json', methods=['GET'])
@ajax_triggered
def get_posts (topic_str):
    """ 
    returns a JSON object with structure {postIDs: [post_id]}
    this function is called via ajax in topic.js
    """
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
        return "topicnotfound", 404

    topic = TopicWrapper(topic)

    if not current_user.may_read(topic.board):
        return "forbidden", 403

    post_ids = map(to_id, PostList(topic_id))

    return jsonify(IDs = post_ids)

@app.route('/topic/<topic_str>/unread.json', methods=['GET'])
@ajax_triggered
def unread_stats (topic_str):
    """ 
    returns a JSON unread stats object for a topic defined by GET parameter topicID
    (structure {unreadCount, firstUnreadID}) this function is called via ajax in topic.js
    """
    topic_id = int(topic_str.split("-")[0])

    topic = Topic.query.get(topic_id)
    if not topic:
        return "topicnotfound", 404

    if current_user.is_anonymous():
        return jsonify(unreadCount = 0, firstUnreadID = None)    

    post_ids = map(to_id, Post.query.filter(Post.topic_id == topic_id))
    read_ids = map(to_post_id, PostRead.query.filter(PostRead.user_id == current_user.id, PostRead.post_id.in_(post_ids)))
    unread_count = Post.query.filter(Post.topic_id == topic_id, not_(Post.id.in_(read_ids))).count()
    first_unread = Post.query.filter(Post.topic_id == topic_id, not_(Post.id.in_(read_ids))).first()

    if not first_unread:
	first_unread_id = None
    else:
	first_unread_id = first_unread.id

    return jsonify(unreadCount = unread_count, firstUnreadID = first_unread_id)    
