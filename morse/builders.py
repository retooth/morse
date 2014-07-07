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

""" this module contains rendering of partial templates, that
    are requested via ajax. 
    for the ajax JSON -> ... <- JSON pipe, check out slots.py
"""

from models import Post, Topic, PostRead, get_my_boards
from mappers import to_id, to_post_id
from wrappers import PostWrapper, TopicWrapper
from flask import request, render_template
from protocols import ajax_triggered
from sqlalchemy import not_

POST_CONTAINER_LIMIT = 5

@app.route('/topic/<topic_str>/certainposts', methods=['POST'])
@ajax_triggered
def certain_posts (topic_str):
    """ 
    renders a number of posts defined by GET json parameter
    this function is called via ajax in topic.js
    """
    topic_id = int(topic_str.split("-")[0])
    topic = Topic.query.get(topic_id)
    if not topic:
        return "topicnotfound", 404

    visible, readable, writable = get_my_boards( get_only_ids = True )
    if not topic.board_id in readable:
        return "forbidden", 403

    posts = []
    for post_id in request.json["IDs"]:
        post = Post.query.get(post_id)
        if not post or post.topic_id != topic_id:
            return "invalidrequest", 400
            break
        post = PostWrapper(post)
        posts.append(post)

    return render_template("partial/posts.html", posts = posts)

@app.route('/board/<board_str>/certaintopics', methods=['POST'])
@ajax_triggered
def certain_topics (board_str):
    """ 
    renders a number of topics defined by GET json parameter
    this function is called via ajax in board.js
    """
    board_id = int(board_str.split("-")[0])
    board = Topic.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    visible, readable, writable = get_my_boards( get_only_ids = True )
    if not board_id in readable:
        return "forbidden", 403

    topics = []
    for topic_id in request.json["IDs"]:
        topic = Topic.query.get(topic_id)
        if not topic or topic.board_id != board_id:
            return "invalidrequest", 400
            break
        topic = TopicWrapper(topic)
        topics.append(topic)

    return render_template("partial/topics.html", topics = topics)

@app.route('/topic/<topic_str>/jump', methods=['GET'])
@ajax_triggered
def jump_to_post (topic_str):
    """ 
    renders a number of posts, that include the post defined in the 
    GET parameter postID. postID can also be set to "first" and "last"
    """
    topic_id = int(topic_str.split("-")[0])
    topic = Topic.query.get(topic_id)
    if not topic:
        return "topicnotfound", 404

    visible, readable, writable = get_my_boards( get_only_ids = True )
    if not topic.board_id in readable:
        return "forbidden", 403

    post_id = request.args.get('postID')

    try:
        post_id = int(post_id)
    except (TypeError, ValueError):
        if post_id.lower() == "first":
            post_id == Post.query.filter(Post.topic_id == topic_id).order_by(Post.id.asc()).first()
        elif post_id.lower() == "last":
            post_id == Post.query.filter(Post.topic_id == topic_id).order_by(Post.id.desc()).first()
        else:
            return "badrequest", 400

    post = Post.query.get(post_id)
    if not post:
        return "postnotfound", 404

    index = Post.query.filter(Post.topic_id == topic_id, Post.id < post.id).count()
    prev_offset = (index // POST_CONTAINER_LIMIT) * POST_CONTAINER_LIMIT

    posts = Post.query.filter(Post.topic_id == topic_id).offset(prev_offset).limit(POST_CONTAINER_LIMIT).all()

    posts = map(PostWrapper, posts)
    return render_template("partial/posts.html", posts = posts, offset = prev_offset, jumpmark = post_id)

@app.route('/buttonbuilder/unread', methods=['GET'])
@ajax_triggered
def build_jump_to_unread_button ():
    try:
        unread_count = int(request.args.get("unreadCount"))
        first_unread_id = int(request.args.get("firstUnreadID"))
    except (TypeError, ValueError):
        return "badrequest", 400
    return render_template("partial/jumptounread.html", unread_count = unread_count, first_unread_id = first_unread_id)
