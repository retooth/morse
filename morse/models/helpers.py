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

def make_url_compatible (string):
    """removes all characters except alphanumeric ones and
    whitespaces, which are substituted with underscores"""
    allowed = []
    for char in string:
        if char.isalnum() or char == " ":
            allowed.append(char)
    allowed = ''.join(allowed)
    return allowed.replace(" ", "_")
