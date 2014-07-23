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

from generators import TopicListGenerator
from flask.ext.login import current_user

class TopicCache (object):

    __monostate = None

    def __init__ (self):
        if not TopicCache.__monostate:
            TopicCache.__monostate = self.__dict__
            self._data = {}
        else:
            self.__dict__ = TopicCache.__monostate

    def fetch (self, board_id):
        key = (current_user.id, board_id)
        if key not in self._data:
            self.refresh(board_id)
        return self._data[key]

    def refresh (self, board_id):
        key = (current_user.id, board_id)
        self._data[key] = [] 
        for topic in TopicListGenerator(board_id):
            self._data[key].append(topic)

