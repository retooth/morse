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

from models import db
from models.discussion import Topic, Post, PostRead, TopicFollow 
from models.filters import TopicFilter, PostFilter
from mappers import to_topic_id, to_post_id
from flask.ext.login import current_user
from sqlalchemy import not_

class ItemFilter (object):
    id = None
    string_identifier = ""

    def filter (self, query):
        raise NotImplementedError(type(self) + " has no filter method")

class TopicItemFilter (ItemFilter):

    def _get_active (self):
        model = TopicFilter.query.filter(TopicFilter.filter_id == self.__class__.id, TopicFilter.user_id == current_user.id).first()
        return model.active

    def _set_active (self, value):
        model = TopicFilter.query.filter(TopicFilter.filter_id == self.__class__.id, TopicFilter.user_id == current_user.id).first()
        model.active = value
        db.session.commit() 

    active = property(fget = _get_active, fset = _set_active)

class UnreadTopicFilter (TopicItemFilter):

    id = 1
    string_identifier = "filter-option-unread"

    def filter (self, query):
        rel = PostRead.query.filter(PostRead.user_id == current_user.id).all()
        read_post_ids = map(to_post_id, rel)
        unread_posts = Post.query.filter(not_(Post.id.in_(read_post_ids))).all()
        #XXX is it smarter to make topic_ids unique at this line?
        topic_ids = map(to_topic_id, unread_posts)
        query = query.filter(Topic.id.in_(topic_ids))
        return query

class FollowedTopicFilter (TopicItemFilter):

    id = 2
    string_identifier = "filter-option-followed"

    def filter (self, query):
        rel = TopicFollow.query.filter(TopicFollow.user_id == current_user.id).all()
        followed_topic_ids = map(to_topic_id, rel)
        query = query.filter(Topic.id.in_(followed_topic_ids))
        return query

class PostItemFilter (ItemFilter):

    def _get_active (self):
        model = PostFilter.query.filter(PostFilter.filter_id == self.__class__.id, PostFilter.user_id == current_user.id).first()
        return model.active

    def _set_active (self, value):
        model = PostFilter.query.filter(PostFilter.filter_id == self.__class__.id, PostFilter.user_id == current_user.id).first()
        model.active = value
        db.session.commit() 

    active = property(fget = _get_active, fset = _set_active)

class UnreadPostFilter (PostItemFilter):

    id = 1
    string_identifier = "filter-option-unread"

    def filter (self, query):
        rel = PostRead.query.filter(PostRead.user_id == current_user.id).all()
        read_post_ids = map(to_id, rel)
        query = query.filter(not_(Post.id.in_(read_post_ids)))
        return query
