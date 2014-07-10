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

class ItemFilter (object):
    id = None
    string_identifier = ""
    template = ""

    def filter (self, query):
        raise NotImplementedError(type(self) + " has no filter method")

class TopicItemFilter (ItemFilter):

    @classmethod
    def install (cls):
        id_registered = TopicFilter.query.filter(TopicFilter.filter_id == cls.id).exists()
        if id_registered:
            raise PluginError("Already found a registered topic filter with id " + str(cls.id) + 
                              "This can have several reasons: 1. The plugin was installed at an " +
                              "earlier time, but was not properly uninstalled. 2. You tried to " +
                              "install this plugin before, but the installation crashed. 3. The " +
                              "plugin supplier chose an id that is in conflict with another plugin " +
                              "or a system reserved id (namely 1-10).")
        user_id_generator = User.query.values(User.id)
        for user_id_oneple in user_id_generator:
            user_id = user_id_oneple[0]
            new_filter = TopicFilter(user_id, cls.id)
            db.session.add(new_filter)

        db.session.commit()

    @classmethod
    def uninstall (cls):
        filters = TopicFilter.query.filter(TopicFilter.filter_id == cls.id).all()
        for filt in filters:
            db.session.delete(filt)
        db.session.commit()

    def _get_active (self):
        model = TopicFilter.query.filter(TopicFilter.filter_id == self.__class__.id, TopicFilter.user_id == current_user.id).first()
        return model.active

    def _set_active (self, value):
        model = TopicFilter.query.filter(TopicFilter.filter_id == self.__class__.id, TopicFilter.user_id == current_user.id).first()
        model.active = value
        db.session.commit() 

    active = property(fget = _get_active, fset = _set_active)

class PostItemFilter (ItemFilter):

    @classmethod
    def install (cls):
        id_registered = PostFilter.query.filter(PostFilter.filter_id == cls.id).exists()
        if id_registered:
            raise PluginError("Already found a registered post filter with id " + str(cls.id) + 
                              "This can have several reasons: 1. The plugin was installed at an " +
                              "earlier time, but was not properly uninstalled. 2. You tried to " +
                              "install this plugin before, but the installation crashed. 3. The " +
                              "plugin supplier chose an id that is in conflict with another plugin " +
                              "or a system reserved id (namely 1-10).")
        user_id_generator = User.query.values(User.id)
        for user_id_oneple in user_id_generator:
            user_id = user_id_oneple[0]
            new_filter = PostFilter(user_id, cls.id)
            db.session.add(new_filter)

        db.session.commit()

    @classmethod
    def uninstall (cls):
        filters = PostFilter.query.filter(PostFilter.filter_id == cls.id).all()
        for filt in filters:
            db.session.delete(filt)
        db.session.commit()

    def _get_active (self):
        model = PostFilter.query.filter(PostFilter.filter_id == self.__class__.id, PostFilter.user_id == current_user.id).first()
        return model.active

    def _set_active (self, value):
        model = PostFilter.query.filter(PostFilter.filter_id == self.__class__.id, PostFilter.user_id == current_user.id).first()
        model.active = value
        db.session.commit() 

    active = property(fget = _get_active, fset = _set_active)

