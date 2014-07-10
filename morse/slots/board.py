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
from flask.ext.login import current_user
from flask import jsonify, request
from ..rights import check_ban, possibly_banned
from ..protocols import ajax_triggered
from ..models import db
from ..models.core import Board
from ..models.discussion import Topic, Post
from generators import TopicListGenerator
from ..wrappers import TopicWrapper, PostWrapper

@app.route('/board/<board_str>/topics.json', methods=['GET'])
@ajax_triggered
def get_topics (board_str):
    """ 
    returns a JSON object with structure {topicIDs: [topic_id]}
    this function is called via ajax in board.js
    """
    board_id = int(board_str.split("-")[0])

    board = Board.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    if not current_user.may_read(board):
        return "forbidden", 403

    topic_ids = []
    for topic_id in TopicListGenerator(board_id):
        topic_ids.append(topic_id)

    return jsonify(IDs = topic_ids)

@app.route('/board/<board_str>/start-topic', methods=['POST'])
@possibly_banned
@ajax_triggered
def start_topic (board_str):
    """ 
    Creates a new topic. Is called by the javascript event
    callback for #docreate
    :param board_id: board in which the new topic 
                     should be started
    :rtype: json 
    """
    board_id = int(board_str.split("-")[0])
    check_ban(board_id)

    board = Board.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    if not current_user.may_post_in(board):
        return "forbidden", 403 

    title = request.json["title"]
    text = request.json["text"]

    topic = Topic(board_id, title)
    # TODO: calculate .interesting
    db.session.add(topic)
    db.session.commit()

    if not current_user.is_anonymous():
        wrapper = TopicWrapper(topic)
        wrapper.follow()

    post = Post(current_user.id, text, topic.id, request.remote_addr)
    db.session.add(post)
    db.session.commit()
    
    if not current_user.is_anonymous():
        post = PostWrapper(post)
        post.read()

    return jsonify(topicId = topic.id)
