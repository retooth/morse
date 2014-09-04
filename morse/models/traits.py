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

class PostTrait (db.Model):
    
    __tablename__ = "post_traits"

    trait_id = db.Column(db.String, primary_key = True)
    relevance = db.Column(db.Integer)

    def __init__ (self, string_identifier):
        self.trait_id = string_identifier
        self.relevance = 0

    @property
    def is_relevant (self):
        return self.relevance > 0

class PostTraitValue (db.Model):

    __tablename__ = "post_trait_values"

    post_id = db.Column(db.ForeignKey("posts.id"), primary_key = True)
    trait_id = db.Column(db.String, primary_key = True);
    value = db.Column(db.Float);

    def __init__ (self, post_id, trait_id, value):
        self.post_id = post_id
        self.trait_id = trait_id
        self.value = value
        
class PostTraitSum (db.Model):

    __tablename__ = "post_trait_sums"

    topic_id = db.Column(db.ForeignKey("topics.id"), primary_key = True)
    trait_id = db.Column(db.String, primary_key = True);
    value = db.Column(db.Float);

    def __init__ (self, topic_id, trait_id, value):
        self.topic_id = topic_id
        self.trait_id = trait_id
        self.value = value
        
