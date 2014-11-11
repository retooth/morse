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
from . import db

class Event (object):

    def __init__ (self, identifier, *args):
        self.identifier = identifier
        self.args = args

class EventDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not EventDispatcher.__monostate:
            EventDispatcher.__monostate = self.__dict__
            self._connections = defaultdict(list)
            self._background_connections = defaultdict(list)
        else:
            self.__dict__ = EventDispatcher.__monostate

    def dispatch (self, event):
        identifier = event.identifier
        for handler in self._connections[identifier]:
            handler(*event.args)
        for background_handler in self._background_connections[identifier]:
            background_handler.delay(*event.args)

    def connect_listener (self, event_identifier, handler):
        self._connections[event_identifier].append(handler)

    def connect_background_listener (self, event_identifier, handler):
        self._background_connections[event_identifier].append(handler)

class RequestRejected (Exception):

    def __init__ (self, returnvalue, statuscode):
        self.returnvalue = returnvalue
        self.statuscode = statuscode

class request_can_be_rejected (object):

    def __init__ (self, f):
        self.f = f
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):
        try:
            return self.f(*args, **kwargs)
        except RequestRejected as r:
            return r.returnvalue, r.statuscode
