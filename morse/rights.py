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
from models.bans import IPBan, UserBan 
from protocols import ajax_triggered
from datetime import datetime

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

    banned = IPBan.query.all()
    for ban in banned:
        if (ip in ban.affected_ips and
           board_id in ban.affected_board_ids and
           not ban.has_expired):
            if ban.is_permanent:
                raise PermaBan(b.reason)
            else:
                raise LimitedBan(b.reason, b.expires)

    banned = UserBan.query.filter(UserBan.user_id == current_user.id).all()
    for ban in banned:
        if not ban.has_expired:
            if ban.is_permanent:
                raise PermaBan(b.reason)
            else:
                raise LimitedBan(b.reason, b.expires)

    # if we have a specific board as argument 
    # ALSO check if a global ban applies
    if board_id != ALL_BOARDS:
        check_ban(ALL_BOARDS)

def is_ajax_triggered (f):

    """ traverses through the function decorator list looking
    for an ajax_triggered decorator. Returns True, if it finds
    one, return False if not """

    while True:
        if type(f) is ajax_triggered:
            return True
            break
        try:
            f = f.f
        except AttributeError:
            return False
            break

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
            if is_ajax_triggered(self.f):
                return "banned", 403
            else:
                return render_template('4xx/403-limitedban.html', current_user = current_user,\
                                       reason = b.reason, expiration = b.expiration), 403
        except PermaBan as b:
            if is_ajax_triggered(self.f):
                return "banned", 403
            else:
                return render_template('4xx/403-permaban.html', current_user = current_user,\
                                       reason = b.reason), 403

class admin_rights_required (object):

    """ 
    admin_rights_required is a function decorator that makes sure,
    that the current user has admin privileges. if not it renders
    the 403 default template and returns a 403 status code
    """

    def __init__ (self, f):
        self.f = f
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):
        if not current_user.may_structure:
            if is_ajax_triggered(self.f):
                return "forbidden", 403
            else:
                return render_template('4xx/403-default.html', current_user = current_user), 403
        return self.f(*args, **kwargs)

def certain_rights_required (may_close_topics = False, may_edit_all_posts = False, may_pin_topics = False, may_ban = False):

    """ 
    certain_rights_required is a function decorator that makes sure,
    that the current user has certain privileges. if not it renders
    the 403 default template and returns a 403 status code

    privileges are set as named parameters, they correspond with
    the privilige flag defined in models.Group

    Example:
    @certain_rights_required(may_close_topics=True)
    def foo ():
        pass
    """

    # Note: this is only a wrapper to allow named argument calling
    # For the inner workings see _certain_rights_required    

    def _wrapper (f):
        return _certain_rights_required(f, may_close_topics, may_edit_all_posts, may_pin_topics, may_ban)
    return _wrapper


class _certain_rights_required (object):

    def __init__ (self, f, may_close_topics, may_edit_all_posts, may_pin_topics, may_ban):
        self.f = f
        self.required = { 'may_close_topics': may_close_topics, 'may_edit_all_posts': may_edit_all_posts, 
                          'may_pin_topics': may_pin_topics, 'may_ban': may_ban }
        # needed for flask integration
        self.__name__ = self.f.__name__

    def _access_denied (self):
        if is_ajax_triggered(self.f):
            return "forbidden", 403
        else:
            return render_template('4xx/403-default.html', current_user = current_user), 403

    def __call__ (self, *args, **kwargs):
        for prop, prop_required in self.required.items():
            if prop_required and not getattr(current_user, prop):
                return self._access_denied()
        return self.f(*args, **kwargs)
