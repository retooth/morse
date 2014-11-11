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
from ..api.dispatchers import PostRatingMethods

class PostRating (db.Model):
    
    __tablename__ = "post_ratings"

    identifier = db.Column(db.String, primary_key = True)
    relevance = db.Column(db.Integer)

    def __init__ (self, identifier):
        self.identifier = identifier
        self.relevance = 0

    @property
    def is_relevant (self):
        return self.relevance > 0

    def determine_value (self, post):
        method = PostRatingMethods().fetch(self.identifier)
        return method.determine_value(post)

class PostRatingValue (db.Model):

    __tablename__ = "post_rating_values"

    post_id = db.Column(db.ForeignKey("posts.id"), primary_key = True)
    rating_id = db.Column(db.ForeignKey("post_ratings.identifier"), primary_key = True)
    value = db.Column(db.Float)

    def __init__ (self, post_id, rating_id, value):
        self.post_id = post_id
        self.rating_id = rating_id
        self.value = value
        
class PostRatingSum (db.Model):

    __tablename__ = "post_rating_sums"

    topic_id = db.Column(db.ForeignKey("topics.id"), primary_key = True)
    rating_id = db.Column(db.ForeignKey("post_ratings.identifier"), primary_key = True)
    value = db.Column(db.Float)

    def __init__ (self, topic_id, rating_id, value):
        self.topic_id = topic_id
        self.rating_id = rating_id
        self.value = value
        
