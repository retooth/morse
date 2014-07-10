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
from models.core import User, Board
from models.discussion import Topic, TopicFollow, Post, PostRead
from flask.ext.login import current_user, AnonymousUserMixin
from collections import defaultdict

class Wrapper (object):

    def __getattr__ (self, attr_name):
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        return getattr(self._inner, attr_name)

class PostWrapper (Wrapper):

    """ A wrapper for the Post model defined in model. It adds the current
    user as context in order to perform user specific alterations (such
    as the post-read-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""

    def __init__ (self, post):
        self._inner = post

    @property
    def creator (self):
        return User.query.get(self.user_id) or AnonymousUserMixin()

    @property
    def isfresh (self):
        postread = PostRead.query.filter(PostRead.user_id == current_user.id,\
                                         PostRead.post_id == self.id).first()

        topic = Topic.query.get(self.topic_id)
        topic = TopicWrapper(topic)
        if not postread and topic.followed:
            return True
        return False

    def read (self):
        if self.isfresh:
            postread = PostRead(current_user.id, self.id)
            db.session.add(postread)
            db.session.commit()

class TopicWrapper (Wrapper):

    """ A wrapper for the Topic model defined in model. It adds the current
    user as context in order to perform user specific alterations (such
    as the followed-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""
    
    def __init__ (self, topic):
        self._inner = topic

    def _getfollowrelation(self):
        return TopicFollow.query.filter(TopicFollow.user_id == current_user.id, \
                                        TopicFollow.topic_id == self.id).first()

    @property
    def followed (self):
        """ signifies, if follow flag is set """
        relation = self._getfollowrelation()
        if relation:
            return True
        return False

    def follow (self):
        """ sets the follow flag for this topic """
        if not self.followed:
            topicfollow = TopicFollow(current_user.id, self.id)
            db.session.add(topicfollow)
            db.session.commit()

    def unfollow (self):
        """ unsets the follow flag for this topic """
        relation = self._getfollowrelation()
        if relation:
            db.session.delete(relation)
            db.session.commit()

    @property
    def isfresh (self):
        """ signifies if topic has posts that haven't been read 
        by current user. returns false, if follow flag is not set."""
        if self.followed:
            onefresh = False
            for post in self.posts:
                onefresh |= post.isfresh
            return onefresh
        return False

    @property
    def posts (self):
        """ gets a list of posts wrapped by PostWrapper """
        posts = Post.query.filter(Post.topic_id == self.id).all()
        return map(PostWrapper, posts)

    @property
    def board (self):
        return Board.query.get(self.board_id)

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
