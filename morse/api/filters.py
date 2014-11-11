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

from ..models import db
from ..models.core import User
from ..models.filters import TopicFilter, PostFilter
from flask.ext.login import current_user
from exceptions import PluginError
from ..patterns import Wrapper

class AbstractItemFilter (object):

    string_identifier = ""
    template = ""

    def change_state (self, state):
        print "at change_state"
        print self._inner
        self._inner.active = state
        db.session.commit()

    def filter (self, query):
        raise NotImplementedError(type(self) + " has no filter method")

class AbstractTopicFilter (Wrapper, AbstractItemFilter):

    @property
    def _inner (self): # getting a bit metaphysical here
        cls = self.__class__
        query = TopicFilter.query.filter(TopicFilter.string_identifier == cls.string_identifier)
        filt = query.filter(TopicFilter.user_id == current_user.id).first()
        if filt is None:
            raise PluginError(cls.__name__ + " was not registered in the database.")
        return filt

    @classmethod
    def install (cls):
        id_registered = TopicFilter.query.filter(TopicFilter.string_identifier == cls.string_identifier).exists()
        if id_registered:
            raise PluginError("Already found a registered topic filter with id " + cls.string_identifier + 
                              "This can have several reasons: 1. The plugin was installed at an " +
                              "earlier time, but was not properly uninstalled. 2. You tried to " +
                              "install this plugin before, but the installation crashed. 3. The " +
                              "plugin supplier chose an id that is in conflict with another plugin ")
        user_id_generator = User.query.values(User.id)
        for user_id_oneple in user_id_generator:
            user_id = user_id_oneple[0]
            new_filter = TopicFilter(user_id, cls.string_identifier)
            db.session.add(new_filter)

        db.session.commit()

    @classmethod
    def uninstall (cls):
        filters = TopicFilter.query.filter(TopicFilter.string_identifier == cls.string_identifier).all()
        for filt in filters:
            db.session.delete(filt)
        db.session.commit()

class AbstractPostFilter (Wrapper, AbstractItemFilter):

    @property
    def _inner (self): # getting a bit metaphysical here
        cls = self.__class__
        query = PostFilter.query.filter(PostFilter.string_identifier == cls.string_identifier)
        filt = query.filter(PostFilter.user_id == current_user.id).first()
        if filt is None:
            raise PluginError(cls.__name__ + " was not registered in the database.")
        return filt

    @classmethod
    def install (cls):
        id_registered = PostFilter.query.filter(PostFilter.string_identifier == cls.string_identifier).exists()
        if id_registered:
            raise PluginError("Already found a registered post filter with id " + cls.string_identifier + 
                              "This can have several reasons: 1. The plugin was installed at an " +
                              "earlier time, but was not properly uninstalled. 2. You tried to " +
                              "install this plugin before, but the installation crashed. 3. The " +
                              "plugin supplier chose an id that is in conflict with another plugin ")

        user_id_generator = User.query.values(User.id)
        for user_id_oneple in user_id_generator:
            user_id = user_id_oneple[0]
            new_filter = PostFilter(user_id, cls.string_identifier)
            db.session.add(new_filter)

        db.session.commit()

    @classmethod
    def uninstall (cls):
        filters = PostFilter.query.filter(PostFilter.string_identifier == cls.string_identifier).all()
        for filt in filters:
            db.session.delete(filt)
        db.session.commit()
