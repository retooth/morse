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
from ..api.dispatchers import PostTraitDispatcher
from sqlalchemy import func
from helpers import make_url_compatible
from core import User, Guest, Board
from traits import PostTraitValue, PostTraitSum
from datetime import datetime

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
    traits_observed = db.Column(db.Boolean, default = False)

    def __init__ (self, user_id, content, topic_id, remote_addr):
        self.user_id = user_id
        self.topic_id = topic_id
        self.content = content
        self.remote_addr = remote_addr

    @property
    def creator (self):
        return User.query.get(self.user_id) or Guest()

    @property
    def topic (self):
        return Topic.query.get(self.topic_id)

    @property
    def is_first_post (self):
        return self.id == self.topic.first_post.id

    @property
    def references (self):
        post_references = PostReference.query.filter(PostReference.post_id == self.id).all()
        for post_reference in post_references:
            post = Post.query.get(post_reference.referenced_post_id)
            yield post

    @property
    def replies (self):
        post_references = PostReference.query.filter(PostReference.referenced_post_id == self.id).all()
        for post_reference in post_references:
            post = Post.query.get(post_reference.post_id)
            yield post

    def calculate_traits (self, post_traits = PostTraitDispatcher()):
        for post_trait in post_traits:
            #FIXME: what if post was once relevant, then
            # irrelevant and now relevant again? this leaves
            # the cache with wrong values or even worse missing ones
            if not post_trait.is_relevant:
                continue
            new_value = post_trait.determine_value(self)
            query = PostTraitValue.query.filter(PostTraitValue.post_id == self.id)
            query = query.filter(PostTraitValue.trait_id == post_trait.trait_id)
            rel = query.first()
            if rel is None:
                rel = PostTraitValue(self.id, post_trait.trait_id, new_value)
                db.session.add(rel)
            else:
                rel.value = new_value

    def observe_traits (self, post_traits = PostTraitDispatcher()):

        assert not self.traits_observed

        for post_trait in post_traits:
            # skip everything if trait is not
            # active
            if not post_trait.is_relevant:
                continue
            # get trait value
            query = PostTraitValue.query.filter(PostTraitValue.post_id == self.id)
            query = query.filter(PostTraitValue.trait_id == post_trait.trait_id)
            rel = query.first()
            if rel is None:
                raise RuntimeError("Tried to observe trait " + post_trait.__class__.__name__ + 
                                   " for post with id " +  self.id + ", but trait value was not calculated")
            value_for_addition = rel.value
            # add it
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == self.topic.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.trait_id).first()
            if sum_rel is None:
                sum_rel = PostTraitSum(self.topic.id, post_trait.trait_id, value_for_addition)
                db.session.add(sum_rel)
            else:
                sum_rel.value = PostTraitSum.value + value_for_addition

        self.traits_observed = True

    def unobserve_traits (self, post_traits = PostTraitDispatcher()):

        assert self.traits_observed

        for post_trait in post_traits:
            # skip everything if trait is not
            # active
            if not post_trait.is_relevant:
                continue
            # get trait value
            query = PostTraitValue.query.filter(PostTraitValue.post_id == self.id)
            query = query.filter(PostTraitValue.trait_id == post_trait.trait_id)
            rel = query.first()
            value_for_subtraction = rel.value
            # subtract it
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == self.topic.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.trait_id).first()
            sum_rel.value = PostTraitSum.value - value_for_subtraction

        self.traits_observed = False

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
    interesting = db.Column(db.Float)
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
        """ a list of all posts in this topic """
        posts = Post.query.filter(Post.topic_id == self.id).all()
        return posts

    @property
    def board (self):
        return Board.query.get(self.board_id)

    @property
    def first_post (self):
        return Post.query.filter(Post.topic_id == self.id).order_by(Post.created_at).first()

    @property
    def last_post (self):
        return Post.query.filter(Post.topic_id == self.id).order_by(Post.created_at.desc()).first()

    @property
    def observed_trait_margin (self):
        # TODO: fetch from config globals
        return 10

    @property
    def next_post_with_obsolete_traits (self):

        """ the post, which falls out of the margin of posts with observed 
        traits the next time a new posts get added to the topic. if the number
        of posts in this topic hasn't exceeded the margin of posts with
        observed traits this property is None

        !!! this property uses the post_count value to determine, whether
        the number of posts exceed the margin. when adding a new post, the
        post_count value must be incremented AFTER this property was used.
        otherwise you will get wrong data and behavior.
        """

        max_interesting_margin = self.observed_trait_margin
        if self.post_count < max_interesting_margin:
            return None

        query = Post.query.filter(Post.topic_id == self.id)
        query = query.filter(Post.traits_observed == True)
        query = query.order_by(Post.created_at)
        return query.first()

    def calculate_interesting_value (self):

        # FIXME: no idea, if this is safe for
        # different timezones
        unix_timedelta = self.last_post.created_at - datetime(1970, 1, 1)
        unix_timestamp = unix_timedelta.days * (24 * 60 * 60) + unix_timedelta.seconds
        interesting = unix_timestamp

        for post_trait in PostTraitDispatcher():
            # skip everything if trait is not
            # active
            if not post_trait.is_relevant:
                continue
            # get sum and calculate average
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == self.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.trait_id).first()
            divisor = min(self.observed_trait_margin, self.post_count)
            average = sum_rel.value / divisor
            interesting += average * post_trait.relevance

        self.interesting = interesting

class FollowedTopic (db.Model):

    """ A many-to-many relation between users and topics. If relations exists
    the user with user_id follow the topic with topic_id. If not, not """

    __tablename__ = "followed_topics"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key=True)

    def __init__ (self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id

class ReadPost (db.Model):

    """ A many-to-many relation between users and posts. If relations exists
    the user with user_id has read the post with post_id. If not, not """

    __tablename__ = "read_posts"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def __init__ (self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

class DiscoveredTopic (db.Model):

    """ A many-to-many relation between users and topics. If relations exists
    the user with user_id has discovered the topic with topic_id. If not, not """

    __tablename__ = "undiscovered_topic"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key=True)

    def __init__ (self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id

class PostReference (db.Model):

    """ A many-to-many relation between posts. If relations exists the post
    with post_id references the post with referenced_post_id """

    __tablename__ = "post_references"
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    referenced_post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def __init__ (self, post_id, referenced_post_id):
        self.post_id = post_id
        self.referenced_post_id = referenced_post_id
