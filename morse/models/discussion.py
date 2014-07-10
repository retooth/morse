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

from . import db
from sqlalchemy import func
from helpers import make_url_compatible

class Post (db.Model):

    """ Model for post entries. Links to user and topic and provides
    metadata (such as creation time and remote address of the poster)
    """

    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    content = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())
    remote_addr = db.Column(db.String)

    def __init__ (self, user_id, content, topic_id, remote_addr):
        self.user_id = user_id
        self.topic_id = topic_id
        self.content = content
        self.remote_addr = remote_addr

class Topic (db.Model):
    
    """ Model for topic entries. Saves title and links to board. It 
    provides also a sticky flag (that moderators can use to put
    the topic permanently on top)
    """

    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    title = db.Column(db.String(100))
    closed = db.Column(db.Boolean)
    sticky = db.Column(db.Boolean)
    # cache
    interesting = db.Column(db.Integer)
    view_count = db.Column(db.Integer)
    post_count = db.Column(db.Integer)
    poster_count = db.Column(db.Integer)

    def __init__ (self, board_id, title):
        self.board_id = board_id
        self.title = title
        self.sticky = False
        self.closed = False
        self.interesting = 0 # TODO: gets set in slots:start_topic
        self.view_count = 0
        self.post_count = 1
        self.poster_count = 1

    @property
    def seostring (self):
        string = str(self.id) + "-" + make_url_compatible(self.title) 
        return string

    @property
    def posts (self):
        """ Returns all posts of this topic :rtype [Post] """    
        return Post.query.filter(Post.topic_id == self.id).all()

class TopicFollow (db.Model):

    """ A many-to-many relation between users and topics. If relations exists
    the user with user_id follow the topic with topic_id. If not, not """

    __tablename__ = "topicfollow"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key=True)

    def __init__ (self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id

class PostRead (db.Model):

    """ A many-to-many relation between users and posts. If relations exists
    the user with user_id has read the post with topic_id. If not, not """

    __tablename__ = "postread"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def __init__ (self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id