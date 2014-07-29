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
from datetime import datetime, timedelta
from core import Board

class Ban (db.Model):
    """ abstract model for bans """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)

    @property
    def short_reason (self):
        reason_length = len(self.reason)
        if reason_length > 25:
            return self.reason[0:25] + "..."
        return self.reason
        
    @property 
    def affected_boards (self):
        for board_id in self.affected_board_ids:
            yield Board.query.get(board_id)

class BannedOn (db.Model):
    """ abstract model of ban <-> board relation """
    __abstract__ = True
    ban_id = db.Column(db.Integer, primary_key=True)

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

class ExpirationMixin (object):

    @property
    def has_expired (self):
        return self.expires < datetime.now()

    @property
    def percentage_of_time_served (self):
        if self.has_expired:
            return 100
        served = self.time_served
        served_in_seconds = served.days * 24 * 60**2 + served.seconds
        duration = self.duration
        duration_in_seconds = duration.days * 24 * 60**2 + duration.seconds
        percentage = (100 * served_in_seconds) / duration_in_seconds
        return percentage

    @property
    def percentage_of_time_left (self):
        return 100 - self.percentage_of_time_served

    @property
    def time_served (self):
        return self.duration - self._time_left

    @property
    def _time_left (self):
        return self.expires - datetime.now()

    @property
    def days_left (self):
        return self._time_left.days

    @property
    def hours_left (self):
        seconds = self._time_left.seconds
        return seconds // 60**2

    @property
    def minutes_left (self):
        seconds = self._time_left.seconds
        seconds_without_hours = seconds % 60**2
        return seconds_without_hours // 60

class PermaIPBan (IPBan):
    """ Use this, if you want to create a permanent IP ban """
    __tablename__ = "permanent_ipbans"

    def __init__ (self, ip_range, reason):
        self._ip_range = ip_range
        self.reason = reason

    @property
    def affected_board_ids (self):
        board_ids = PermaIPBannedOn.query.filter(PermaIPBannedOn.ban_id == self.id).values(PermaIPBannedOn.board_id)
        return board_ids


class PermaIPBannedOn (BannedOn):
    __tablename__ = "permanent_ipbanned_on"
    board_id = db.Column(db.Integer, primary_key=True)

class LimitedIPBan (IPBan, ExpirationMixin):
    """ Use this, if you want to create a limited IP ban """
    __tablename__ = "limited_ipbans"
    duration = db.Column(db.Interval)
    expires = db.Column(db.DateTime)

    def __init__ (self, ip_range, reason, duration_in_days):
        self._ip_range = ip_range
        self.reason = reason
        self.duration = timedelta(days = duration_in_days)
        self.expires = datetime.now() + self.duration

    @property
    def affected_board_ids (self):
        board_ids = LimitedIPBannedOn.query.filter(LimitedIPBannedOn.ban_id == self.id).values(LimitedIPBannedOn.board_id)
        return board_ids

class LimitedIPBannedOn (BannedOn):
    __tablename__ = "limited_ipbanned_on"

class PermaUserBan (Ban):
    """ Use this, if you want to create a permanent user ban """
    __tablename__ = "permanent_userbans"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__ (self, user_id, reason):
        self.user_id = user_id
        self.reason = reason

    @property
    def affected_board_ids (self):
        board_ids = PermaUserBannedOn.query.filter(PermaUserBannedOn.ban_id == self.id).values(PermaUserBannedOn.board_id)
        return board_ids

class PermaUserBannedOn (BannedOn):
    __tablename__ = "permanent_userbanned_on"
    board_id = db.Column(db.Integer, primary_key=True)

class LimitedUserBan (Ban, ExpirationMixin):
    """ Use this, if you want to create a limited user ban """
    __tablename__ = "limited_userbans"
    duration = db.Column(db.Interval)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__ (self, user_id, reason, duration_in_days):
        self.user_id = user_id
        self.reason = reason
        self.duration = timedelta(days = duration_in_days)
        self.expires = datetime.now() + self.duration

    @property
    def affected_board_ids (self):
        board_ids = LimitedUserBannedOn.query.filter(LimitedUserBannedOn.ban_id == self.id).values(LimitedUserBannedOn.board_id)
        return board_ids

class LimitedUserBannedOn (BannedOn):
    __tablename__ = "limited_userbanned_on"
    board_id = db.Column(db.Integer, primary_key=True)
