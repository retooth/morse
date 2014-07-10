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

from ..models.discussion import Post, Topic, PostRead
from ..models.core import Board
from ..wrappers import PostWrapper, TopicWrapper
from flask import request, render_template
from ..protocols import ajax_triggered
from sqlalchemy import not_
from flask.ext.login import current_user

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

    topic = TopicWrapper(topic)
    if not current_user.may_read(topic.board):
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
    board = Board.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    if not current_user.may_read(board):
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

