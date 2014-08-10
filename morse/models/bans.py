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
from core import Board, User

class Ban (db.Model):

    """ Ban is an abstract model for IPBan and UserBan. It provides
    methods to check for affected boards and some to get different parts 
    of the ban duration """

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)
    duration = db.Column(db.Interval)
    expiration_date = db.Column(db.DateTime)

    def __init__ (self, reason, duration_in_days = None):
        self.reason = reason
        if duration_in_days:
            self.duration = timedelta(days = duration_in_days)
            self.expiration_date = datetime.now() + self.duration
    
    def applies_to (self, board):
        """ signifies whether a ban applies to a certain board """
        affected = self.affected_board_ids
        return board.id in affected
        
    @property 
    def affected_boards (self):
        """ a list of all affected boards """
        for board_id in self.affected_board_ids:
            yield Board.query.get(board_id)

    @property
    def is_permanent (self):
        return self.expiration_date is None

    def update_duration_in_days (self, duration):
        if duration is None:
            self.duration = None
            self.expiration_date = None
        else:
            if self.is_permanent:
                old_beginning = datetime.now()
            else:
                old_beginning = self.expiration_date - self.duration
            self.duration = timedelta(days = duration)
            self.expiration_date = old_beginning + self.duration
    
    duration_in_days = property(fset = update_duration_in_days)

    @property
    def has_expired (self):
        if self.is_permanent:
            return False
        return self.expiration_date < datetime.now()

    @property
    def percentage_of_time_served (self):
        if self.is_permanent:
            return 0
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
        """ a timedelta object that signifies the 
        served time (only possible on limited bans) """
        if self.is_permanent:
            raise TypeError("this method is not available on permanent bans")
        return self.duration - self.time_left

    @property
    def time_left (self):
        """ a timedelta object that signifies the 
        time left to serve (only possible on limited bans) """
        if self.is_permanent:
            raise TypeError("this method is not available on permanent bans")
        return self.expiration_date - datetime.now()

    @property
    def days_left (self):
        """ an integer that signifies the number of days
        left to serve (only possible on limited bans) """
        if self.is_permanent:
            raise TypeError("this method is not available on permanent bans")
        return self.time_left.days

    @property
    def hours_left (self):
        """ an integer that signifies the number of hours
        left to serve (only possible on limited bans) 

        !!! this attribute DOES NOT signify the absolute
        number of hours left, but rather the numbers of
        hours left modulo 24
        """
        if self.is_permanent:
            raise TypeError("this method is not available on permanent bans")
        seconds = self.time_left.seconds
        return seconds // 60**2

    @property
    def minutes_left (self):
        """ an integer that signifies the number of minutes
        left to serve (only possible on limited bans) 

        !!! this attribute DOES NOT signify the absolute
        number of minutes left, but rather the numbers of
        minutes left modulo 60
        """
        if self.is_permanent:
            raise TypeError("this method is not available on permanent bans")
        seconds = self.time_left.seconds
        seconds_without_hours = seconds % 60**2
        return seconds_without_hours // 60

class IPBan (Ban):

    """ model for IP bans """

    __tablename__ = "ip_bans"

    ip_range = db.Column(db.String)

    def __init__ (self, ip_range, reason, duration_in_days = None):
        Ban.__init__(self, reason, duration_in_days)
        self.ip_range = ip_range

    @property
    def affected_ips (self):
        """ use this property instead of ip_range. it provides a
        iptools.IpRange object instead of a simple string, which
        means you can perform containment operations (e.g.
        "my_ip in ban.ip_range" and the like) """
        return IpRange(self.ip_range)

    @property
    def affected_board_ids (self):
        """ an ID list of all affected boards """
        query = IPBannedOn.query
        query = query.filter(IPBannedOn.ban_id == self.id)
        board_id_generator = query.values(IPBannedOn.board_id)
        board_ids = [oneple[0] for oneple in board_id_generator]
        return board_ids

class IPBannedOn (db.Model):

    """ A relation between ip bans and boards, that signify
    which boards are affected by a certain ip ban """

    __tablename__ = "ip_banned_on"

    ban_id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, primary_key=True)

    def __init__ (self, board_id, ban_id):
        self.board_id = board_id
        self.ban_id = ban_id

class UserBan (Ban):

    """ model for user bans """

    user_id = db.Column(db.ForeignKey("users.id"))

    def __init__ (self, user_id, reason, duration_in_days = None):
        Ban.__init__(self, reason, duration_in_days)
        self.user_id, user_id

    @property
    def affected_user (self):
        return User.query.get(self.user_id)

    @property
    def affected_board_ids (self):
        """ an ID list of all affected boards """
        query = UserBannedOn.query
        query = query.filter(UserBannedOn.ban_id == self.id)
        board_id_generator = query.values(UserBannedOn.board_id)
        board_ids = [oneple[0] for oneple in board_id_generator]
        return board_ids


class UserBannedOn (db.Model):

    """ A relation between user bans and boards, that signify
    which boards are affected by a certain user ban """

    __tablename__ = "user_banned_on"

    ban_id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, primary_key=True)

    def __init__ (self, board_id, ban_id):
        self.board_id = board_id
        self.ban_id = ban_id
