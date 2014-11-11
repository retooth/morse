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

class FormatToolDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not FormatToolDispatcher.__monostate:
            FormatToolDispatcher.__monostate = self.__dict__
            self._tools = []
        else:
            self.__dict__ = FormatToolDispatcher.__monostate

    def attach (self, filt):
        # TODO: check for database inconsistency
        self._tools.append(filt)

    @property
    def is_empty(self):
        return self._tools == []

    def __iter__ (self):
        for tool_blueprint in self._tools:
            tool = tool_blueprint()
            yield tool

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

class PostRatingMethods (object):

    __monostate = None

    def __init__ (self):
        if not PostRatingMethods.__monostate:
            PostRatingMethods.__monostate = self.__dict__
            self._methods = {}
        else:
            self.__dict__ = PostRatingMethods.__monostate

    def attach (self, method):
        identifier = method.identifier
        self._methods[identifier] = method

    @property
    def identifiers (self):
        return self._methods.keys()

    def fetch (self, identifier):
        if identifier not in self._methods:
            raise InconsistencyError("Post rating with identifier " + identifier + " has no method associated." + \
                                     "This error mostly happens, when a plugin is deleted from the file system " + \
                                     "without proper uninstallment.")
        return self._methods[identifier]
