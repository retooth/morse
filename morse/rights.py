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

from flask import request, render_template
from flask.ext.login import current_user
from models import LimitedIPBan, PermaIPBan, LimitedUserBan, PermaUserBan

ALL_BOARDS = 0

class LimitedBan (StandardError):
    
    def __init__ (self, reason, expiration):
        self.reason = reason
        self.expiration = expiration

class PermaBan (StandardError):

    def __init__ (self, reason):
        self.reason = reason

def check_ban (board_id = ALL_BOARDS):

    """
    Raises a UserBanned Exception, if a matching rule is found in the database.
    In general users can be banned on certain boards or globally, either by
    username or ip rules. if check_ban is called without an argument, it
    checks for global bans only. If no rule applies the function just
    exits returning none
    """

    ip = request.remote_addr

    banned = LimitedIPBan.query.filter(LimitedIPBan.board_id.like(board_id)).all()
    for b in banned:
        if ip in b.ip_range:
            raise LimitedBan(b.reason, b.expires)

    banned = PermaIPBan.query.filter(PermaIPBan.board_id.like(board_id)).all()
    for b in banned:
        if ip in b.ip_range:
            raise PermaBan(b.reason)

    banned = LimitedUserBan.query.filter(LimitedUserBan.board_id.like(board_id)).all()
    for b in banned:
        if current_user.id == b.user_id:
            raise LimitedBan(b.reason, b.expires)

    banned = PermaUserBan.query.filter(PermaUserBan.board_id.like(board_id)).all()
    for b in banned:
        if current_user.id == b.user_id:
            raise PermaBan(b.reason)

    # if we have a specific board as argument 
    # ALSO check if a global ban applies
    if board_id != ALL_BOARDS:
        check_ban(ALL_BOARDS)


class possibly_banned (object):

    """ 
    possibly_banned is a function decorator that serves as a exception 
    handler for views, which use the check_ban function defined above. 
    It renders the banned template and adds additional information 
    propagated by the exception (such as: reason, expiration date, etc)
    """
    
    def __init__ (self, f):
        self.f = f
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):
        try:
            return self.f(*args, **kwargs)
        except LimitedBan as b:
            # TODO: factor expiration timestamp in human readable
            # delta ("1 week, 4 days, 10 hours, 5 seconds to go")
            return render_template('limitedban.html', current_user = current_user,\
                                   reason = b.reason, expiration = b.expiration)
        except PermaBan as b:
            return render_template('permaban.html', current_user = current_user,\
                                   reason = b.reason)

class admin_rights_required (object):

    """ 
    admin_rights_required is a function decorator that makes sure,
    that the current user has admin privileges. if not it renders
    the accessdenied template and returns a 403 status code
    """

    def __init__ (self, f):
        self.f = f
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):
        if not current_user.may_structure:
            return render_template('accessdenied.html', current_user = current_user), 403
        return self.f(*args, **kwargs)