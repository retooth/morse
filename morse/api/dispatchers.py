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

from collections import defaultdict

# for later use
class DataDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not DataDispatcher.__monostate:
            DataDispatcher.__monostate = self.__dict__
            self._data = defaultdict(list)
        else:
            self.__dict__ = Dispatcher.__monostate

    def attach (self, section, item):
        self._data[section].append(item)

    def dispatch (self, section):
        return self._data[section]

class TopicFilterDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not TopicFilterDispatcher.__monostate:
            TopicFilterDispatcher.__monostate = self.__dict__
            self._filters = []
        else:
            self.__dict__ = TopicFilterDispatcher.__monostate

    def attach (self, filt):
        # TODO: check for database inconsistency
        self._filters.append(filt)

    @property
    def is_empty(self):
        return self._filters == []

    def __iter__ (self):
        for filter_blueprint in self._filters:
            filt = filter_blueprint()
            yield filt

class PostFilterDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not PostFilterDispatcher.__monostate:
            PostFilterDispatcher.__monostate = self.__dict__
            self._filters = []
        else:
            self.__dict__ = PostFilterDispatcher.__monostate

    def attach (self, filt):
        # TODO: check for database inconsistency
        self._filters.append(filt)

    @property
    def is_empty(self):
        return self._filters == []

    def __iter__ (self):
        for filter_blueprint in self._filters:
            filt = filter_blueprint()
            yield filt
