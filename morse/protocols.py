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

class ajax_triggered (object):

    """ 
    ajax_triggered is a function decorator that identifies a view
    as triggered by ajax. this is necessary for function decorators,
    that handle exceptions, such as possible_banned, which will return
    error strings instead of templates, when ajax_triggered is set.
    
    WARNING: exception decorators recognize this decorator by traversing
    through the f attribute. This means, that ajax_triggered has
    to be ALWAYS the last decorator in a decorator list (or at least
    it has to be defined AFTER the decorators that use it)
    """
    
    def __init__ (self, f):
        self.f = f
        # needed for flask integration
        self.__name__ = self.f.__name__

    def __call__ (self, *args, **kwargs):
        return self.f(*args, **kwargs)
