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
from flask.ext.login import current_user, login_required
from flask import jsonify, request
from ..rights import check_ban, possibly_banned
from ..validators import json_input, String
from ..protocols import ajax_triggered
from ..models import db
from ..models.core import Board
from ..models.discussion import Topic, Post, DiscoveredTopic
from ..generators import TopicListGenerator
from ..wrappers import TopicWrapper, PostWrapper, BoardWrapper
from ..cache import TopicCache
from sqlalchemy import not_

@app.route('/board/<board_str>/refresh-topic-cache', methods=['GET'])
@ajax_triggered
def refresh_topic_cache (board_str):
    """ 
    updates the topic cache for current user. this function
    is called via ajax in board.js when filter or sorting
    options change
    """
    board_id = int(board_str.split("-")[0])

    board = Board.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    cache = TopicCache()
    cache.refresh(board_id)
    return ""

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
    for topic in TopicListGenerator(board_id):
        topic_ids.append(topic.id)

    cache = TopicCache()
    cache.refresh(board_id) 

    return jsonify(IDs = topic_ids)

@app.route('/board/<board_str>/start-topic', methods=['POST'])
@possibly_banned
@ajax_triggered
@json_input({"title": String(), "text": String()})
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
    db.session.add(topic)
    db.session.commit()

    if not current_user.is_anonymous():
        wrapper = TopicWrapper(topic)
        wrapper.follow()

    post = Post(current_user.id, text, topic.id, request.remote_addr)
    db.session.add(post)
    db.session.commit()
  
    post.calculate_traits() 
    db.session.commit()

    post.observe_traits()
    db.session.commit()

    topic.calculate_interesting_value()
    db.session.commit()

    if not current_user.is_anonymous():
        post = PostWrapper(post)
        post.read()

    cache = TopicCache()
    cache.refresh(board_id)

    return jsonify(topicId = topic.id)

@app.route('/board/<board_str>/follow', methods=['POST'])
@login_required
@ajax_triggered
def follow_board (board_str):
    """ 
    follows a board. this function is called via ajax
    by the click event handler for #follow-board in board.js
    """
    board_id = int(board_str.split("-")[0])

    board = Board.query.get(board_id)
    if not board:
        return "nosuchboard", 400
 
    board = BoardWrapper(board)
    board.follow()
    return ""

@app.route('/board/<board_str>/unfollow', methods=['POST'])
@login_required
@ajax_triggered
def unfollow_board (board_str):
    """ 
    unfollows a board. this function is called via ajax
    by the click event handler for #follow-board in board.js
    """
    board_id = int(board_str.split("-")[0])

    board = Board.query.get(board_id)
    if not board:
        return "nosuchboard", 400

    board = BoardWrapper(board)
    board.unfollow()
    return ""

@app.route('/board/<board_str>/undiscovered.json', methods=['GET'])
@ajax_triggered
def undiscovered_topic_stats (board_str):
    """ 
    returns a JSON undiscovered topic stats object for a board defined by board_str
    (structure {unreadCount, firstUnreadID}) this function is called via ajax in index.js
    """
    board_id = int(board_str.split("-")[0])

    board = Board.query.get(board_id)
    if not board:
        return "boardnotfound", 404

    if current_user.is_anonymous():
        return jsonify(undiscoveredCount = 0, firstUndiscoveredID = None)    

    topic_id_generator = Topic.query.filter(Topic.board_id == board_id).values(Topic.id)
    topic_ids = [oneple[0] for oneple in topic_id_generator] 

    discovered_ids_generator = DiscoveredTopic.query.filter(DiscoveredTopic.user_id == current_user.id, 
                                                            DiscoveredTopic.topic_id.in_(topic_ids)).values(DiscoveredTopic.topic_id)
    discovered_ids = [oneple[0] for oneple in discovered_ids_generator] 
    
    undiscovered_count = Topic.query.filter(Topic.board_id == board_id, not_(Topic.id.in_(discovered_ids))).count()
    first_undiscovered = Topic.query.filter(Topic.board_id == board_id, not_(Topic.id.in_(discovered_ids))).first()

    if not first_undiscovered:
        first_undiscovered_id = None
    else:
        first_undiscovered_id = first_undiscovered.id

    return jsonify(undiscoveredCount = undiscovered_count, firstUndiscoveredID = first_undiscovered_id)    
