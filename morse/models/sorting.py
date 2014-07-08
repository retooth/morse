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
from enum import MOST_INTERESTING

class TopicSortingPreference (db.Model):
    """ user preference for topic sorting """
    __tablename__ = "topic_sorting_preferences"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    preference_id = db.Column(db.Integer)
    def __init__ (self, user_id, preference_id = MOST_INTERESTING):
        self.user_id = user_id
        self.preference_id = preference_id
