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

from flask.ext.login import current_user
from sqlalchemy import not_
from api.dispatchers import TopicFilterDispatcher, PostFilterDispatcher
from models.discussion import Post, Topic
from models import db

def TopicListGenerator (board_id):
    query = Topic.query.filter(Topic.board_id == board_id) 
    dispatcher = TopicFilterDispatcher()

    for topic_filter in current_user.active_topic_filters:
        for filt in dispatcher:
            if topic_filter == filt.string_identifier:
                query = filt.filter(query)

    sticky = query.filter(Topic.sticky == True).all()

    # TODO: sorting preferences
    # TODO: guest preferences (cookies)
    not_sticky = query.filter(Topic.sticky == False).all()

    topics = sticky + not_sticky

    return topics

def PostListGenerator (topic_id):

    query = Post.query.filter(Post.topic_id == topic_id) 
    dispatcher = PostFilterDispatcher()

    for post_filter in current_user.active_post_filters:
        for filt in dispatcher:
            if post_filter == filt.string_identifier:
                query = filt.filter(query)

    return query.order_by(Post.created_at).all()

