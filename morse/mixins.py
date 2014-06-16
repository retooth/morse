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

from flask.ext.login import AnonymousUserMixin
from models import get_my_boards

class GuestMixin (AnonymousUserMixin):

    @property
    def id (self):
        return 0

    def may_post_in (self, board):
        """ signifies if a user may post in a specific board. This is used in
        in templates to decide, if the post dialog is shown"""
        visible, readable, writable = get_my_boards(user = self, get_only_ids = True)
        return board.id in writable
    
