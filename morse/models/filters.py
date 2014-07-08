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

class BoardFilter (db.Model):

    """ board filter for registered users """

    __tablename__ = "board_filters"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    filter_id = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    def __init__ (self, user_id, filter_id, active = False):
        self.user_id = user_id
        self.filter_id = filter_id
        self.active = active

class TopicFilter (db.Model):

    """ topic filter for registered users """

    __tablename__ = "topic_filters"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    filter_id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean)

    def __init__ (self, user_id, filter_id, active = False):
        self.user_id = user_id
        self.filter_id = filter_id
        self.active = active

class PostFilter (db.Model):

    """ post filter for registered users """

    __tablename__ = "post_filters"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    filter_id = db.Column(db.Integer)
    active = db.Column(db.Boolean)

    def __init__ (self, user_id, filter_id, active = False):
        self.user_id = user_id
        self.filter_id = filter_id
        self.active = active
