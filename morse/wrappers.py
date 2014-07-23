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
from models.core import User, Board, Guest, FollowedBoard
from models.discussion import Topic, FollowedTopic, Post, ReadPost, DiscoveredTopic
from flask.ext.login import current_user
from collections import defaultdict
from cache import TopicCache

class Wrapper (object):

    def __getattr__ (self, attr_name):
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        return getattr(self._inner, attr_name)

class PostWrapper (Wrapper):

    """ A wrapper for the Post model defined in models.discussion. It adds the current
    user as context in order to perform user specific alterations (such
    as the post-read-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""

    def __init__ (self, post):
        self._inner = post

    @property
    def isfresh (self):
        post_is_read = ReadPost.query.filter(ReadPost.user_id == current_user.id,\
                                             ReadPost.post_id == self.id).first()

        topic = Topic.query.get(self.topic_id)
        topic = TopicWrapper(topic)
        if not post_is_read and topic.followed:
            return True
        return False

    @property
    def topic (self):
        topic = Topic.query.get(self.topic_id)
        return TopicWrapper(topic)

    def read (self):
        if self.isfresh:
            relation = ReadPost(current_user.id, self.id)
            db.session.add(relation)
            db.session.commit()

class TopicWrapper (Wrapper):

    """ A wrapper for the Topic model defined in models.discussion It adds the current
    user as context in order to perform user specific alterations (such
    as the followed-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""
    
    def __init__ (self, topic):
        self._inner = topic

    def _get_follow_relation(self):
        return FollowedTopic.query.filter(FollowedTopic.user_id == current_user.id, \
                                          FollowedTopic.topic_id == self.id).first()

    @property
    def followed (self):
        """ signifies, if follow flag is set """
        relation = self._get_follow_relation()
        if relation:
            return True
        return False

    def follow (self):
        """ sets the follow flag for this topic """
        if not self.followed:
            relation = FollowedTopic(current_user.id, self.id)
            db.session.add(relation)
            db.session.commit()

    def unfollow (self):
        """ unsets the follow flag for this topic """
        relation = self._get_follow_relation()
        if relation:
            db.session.delete(relation)
            db.session.commit()

    @property
    def isfresh (self):
        topic_entry_is_discovered = DiscoveredTopic.query.filter(DiscoveredTopic.user_id == current_user.id,\
                                                                 DiscoveredTopic.topic_id == self.id).first()

        board = Board.query.get(self.board_id)
        board = BoardWrapper(board)
        if not topic_entry_is_discovered and board.followed:
            return True
        return False

    def discover (self):
        if self.isfresh:
            relation = DiscoveredTopic(current_user.id, self.id)
            db.session.add(relation)
            db.session.commit()

    @property
    def posts (self):
        """ gets a list of posts wrapped by PostWrapper """
        posts = Post.query.filter(Post.topic_id == self.id).all()
        return map(PostWrapper, posts)

    @property
    def board (self):
        board = Board.query.get(self.board_id)
        return BoardWrapper(board)

    @property
    def next (self):
        cache = TopicCache()
        topics = cache.fetch(self.board_id)
        topics_count = len(topics)
        for index, topic in enumerate(topics):
            if topic.id == self.id:
                if index == (topics_count - 1):
                    return TopicWrapper(topics[0])
                    break
                else:
                    return TopicWrapper(topics[index + 1])
                    break
        return TopicWrapper(topics[0])

    @property
    def previous (self):
        cache = TopicCache()
        topics = cache.fetch(self.board_id)
        topics_count = len(topics)
        for index, topic in enumerate(topics):
            if topic.id == self.id:
                if index == 0:
                    return TopicWrapper(topics[topics_count - 1])
                    break
                else:
                    return TopicWrapper(topics[index - 1])
                    break
        return TopicWrapper(topics[0])

    def __getitem__ (self, val):
        """ gets a single post or a slice of posts """
        if type(val) is slice:
            if slice.step:
                raise ValueError("Slice steps are not supported")
            start = slice.start
            if start < 0:
                start = self.post_count + start
            if slice.stop:
                limit = slice.stop - slice.start
            else:
                limit = 0
            posts = Post.query.filter(Post.topic_id == self.id).offset(start).limit(limit).all()
            return map(PostWrapper, posts)

class BoardWrapper (Wrapper):

    """ A wrapper for the Board model defined in models.core. It adds the current
    user as context in order to perform user specific alterations (such
    as the followed-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""
    
    def __init__ (self, board):
        self._inner = board

    def _get_follow_relation(self):
        return FollowedBoard.query.filter(FollowedBoard.user_id == current_user.id, \
                                          FollowedBoard.board_id == self.id).first()

    @property
    def followed (self):
        """ signifies, if follow flag is set """
        relation = self._get_follow_relation()
        if relation:
            return True
        return False

    def follow (self):
        """ sets the follow flag for this board """
        if not self.followed:
            relation = FollowedBoard(current_user.id, self.id)
            db.session.add(relation)
            db.session.commit()

    def unfollow (self):
        """ unsets the follow flag for this board """
        relation = self._get_follow_relation()
        if relation:
            db.session.delete(relation)
            db.session.commit()

    @property
    def topics (self):
        """ gets a list of topics wrapped by TopicWrapper """
        topics = Topic.query.filter(Topic.board_id == self.id).all()
        return map(TopicWrapper, topics)

    def __getitem__ (self, val):
        """ gets a single topic or a slice of topics """
        if type(val) is slice:
            if slice.step:
                raise ValueError("Slice steps are not supported")
            start = slice.start
            if start < 0:
                start = self.topic_count + start
            if slice.stop:
                limit = slice.stop - slice.start
            else:
                limit = 0
            topics = Topic.query.filter(Topic.board_id == self.id).offset(start).limit(limit).all()
            return map(TopicWrapper, topics)
