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

def to_id (modelobject):
    return modelobject.id

def to_user_id (modelobject):
    return modelobject.user_id

def to_post_id (modelobject):
    return modelobject.post_id

def to_topic_id (modelobject):
    return modelobject.topic_id

def to_creation_timestamp (modelobject):
    return modelobject.created_at

def to_filter_id (modelobject):
    return modelobject.filter_id


