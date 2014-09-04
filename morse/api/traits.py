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
from ..models.traits import PostTraitValue, PostTrait
from exceptions import PluginError
from ..patterns import Wrapper

"""
this module implements base classes for topic and post traits.

traits are content and meta statistics about topics and posts,
that influence the "interesting value" of topics. in morse
admins can pick traits that are valued by the community and
topics get sorted accordingly. available default traits are
e.g. the eloquency of a post, the community interest measured
in unique posters or the amount of images in a post.
"""

class AbstractPostTrait (Wrapper):

    @property
    def _inner (self): # getting a bit metaphysical here
        cls = self.__class__
        trait = PostTrait.query.get(cls.string_identifier)
        if trait is None:
            raise PluginError(cls.__name__ + " was not registered in the database.")
        return trait

#    @classmethod
#    def install (cls):
#        id_registered = PostTraitValue.query.filter(PostTraitValue.trait_id == cls.id).exists()
#        # TODO: (also on filters): check for reserved ids and make them 1-100
#        if id_registered:
#            raise PluginError("Already found a registered post trait with id " + str(cls.id) + 
#                              "This can have several reasons: 1. The plugin was installed at an " +
#                              "earlier time, but was not properly uninstalled. 2. You tried to " +
#                              "install this plugin before, but the installation crashed. 3. The " +
#                              "plugin supplier chose an id that is in conflict with another plugin " +
#                              "or a system reserved id (namely 1-10).")
#        posts = Post.query.all()
#        for post in posts:
#            temp_object = cls()
#            value = temp_object.determine_value(post)
#            new_trait_value = TopicTraitValue(post.id, cls.id, value)
#            db.session.add(new_trait_value)
#
#        db.session.commit()
#
#    @classmethod
#    def uninstall (cls):
#        trait_values = PostTraitValue.query.filter(PostTraitValue.filter_id == cls.id).all()
#        for trait_value in trait_values:
#            db.session.delete(trait_value)
#        db.session.commit()

    def determine_value (self, post):
        raise NotImplementedError(self.__class__.__name__ + " needs a determine_value method")
