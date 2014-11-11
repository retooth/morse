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

"""
this module implements base classes for topic and post rating methods.

ratings influence the "interesting value" of topics. in morse
admins can define which contribution behavior is valued by 
the community and topics get sorted accordingly. available default 
rating methods are e.g. the eloquency of a post, the community 
interest measured in unique posters or the amount of images in a post.
"""

class PostRatingMethod (object):

    identifier = ""

    def determine_value (self, post):
        raise NotImplementedError(self.__class__.__name__ + " needs a determine_value method")
