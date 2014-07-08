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
from iptools import IpRange

class Ban (db.Model):
    """ abstract model for bans """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)

class IPBan (Ban):
    """ abstract model for IP bans """
    __abstract__ = True
    _ip_range = db.Column(db.String)

    @property
    def ip_range (self):
        """ use this property instead of _ip_range. it provides a
        iptools.IpRange object instead of a simple string, which
        means you can perform containment operations (e.g.
        "my_ip in ban.ip_range" and the like) """
        return IpRange(self._ip_range)

class PermaIPBan (IPBan):
    """ Use this, if you want to create a permanent IP ban """
    __tablename__ = "permanent_ipbans"
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, ip_range, board_id, reason):
        self._ip_range = ip_range
        self.board_id = board_id
        self.reason = reason

class LimitedIPBan (IPBan):
    """ Use this, if you want to create a limited IP ban """
    __tablename__ = "limited_ipbans"
    expires = db.Column(db.DateTime)
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, ip_range, board_id, reason, expires):
        self._ip_range = ip_range
        self.board_id = board_id
        self.reason = reason
        self.expires = expires

class PermaUserBan (Ban):
    """ Use this, if you want to create a permanent user ban """
    __tablename__ = "permanent_userbans"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, user_id, board_id, reason):
        self.user_id = user_id
        self.board_id = board_id
        self.reason = reason

class LimitedUserBan (Ban):
    """ Use this, if you want to create a limited user ban """
    __tablename__ = "limited_userbans"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, user_id, board_id, reason, expires):
        self.user_id = user_id
        self.board_id = board_id
        self.reason = reason
        self.expires = expires
