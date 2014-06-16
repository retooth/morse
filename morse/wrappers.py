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

from models import TopicFollow, PostRead, Topic, Board, User, db
from flask.ext.login import current_user, AnonymousUserMixin
from collections import defaultdict

class PostWrapper (object):

    """ A wrapper for the Post model defined in model. It adds the current
    user as context in order to perform user specific alterations (such
    as the post-read-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""

    def __init__ (self, post):
        self.post = post

    @property
    def user_id (self):
        return self.post.user_id

    @property
    def creator (self):
        return User.query.get(self.user_id) or AnonymousUserMixin()

    @property
    def remote_addr (self):
        return self.post.remote_addr

    @property
    def id (self):
        return self.post.id
    
    @property
    def topic_id (self):
        return self.post.topic_id

    @property
    def content (self):
        return self.post.content

    @property
    def created_at (self):
        return self.post.created_at

    @property
    def isfresh (self):
        postread = PostRead.query.filter(PostRead.user_id.like(current_user.id),\
                                         PostRead.post_id.like(self.post.id)).first()

        topic = Topic.query.filter(Topic.id.like(self.topic_id)).first()
        topic = TopicWrapper(topic)
        if not postread and topic.followed:
            return True
        return False

    def read (self):
        if self.isfresh:
            postread = PostRead(current_user.id, self.id)
            db.session.add(postread)
            db.session.commit()

class TopicWrapper (object):

    """ A wrapper for the Topic model defined in model. It adds the current
    user as context in order to perform user specific alterations (such
    as the followed-flag). It also provides some convenient functions and acts as
    a proxy for the wrapped post. It does however NOT inherit from the model,
    so saving it to the db session will fail"""
    
    def __init__ (self, topic):
        self.topic = topic

    def _getfollowrelation(self):
        return TopicFollow.query.filter(TopicFollow.user_id.like(current_user.id), \
                                        TopicFollow.topic_id.like(self.topic.id)).first()

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
            topicfollow = TopicFollow(current_user.id, self.topic.id)
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
        return map(PostWrapper, self.topic.posts)

    @property
    def title (self):
        return self.topic.title

    @property
    def board_id (self):
        return self.topic.board_id

    @property
    def board (self):
        return Board.query.get(self.board_id)

    @property
    def id (self):
        return self.topic.id

    @property
    def closed(self):
        return self.topic.closed

    @property
    def sticky(self):
        return self.topic.sticky
