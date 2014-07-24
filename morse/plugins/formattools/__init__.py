#!/usr/bin/python

#    This plugin is part of Morse.
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

from morse.api.dispatchers import FormatToolDispatcher
from formats import FormatBold, FormatItalic, FormatQuote, FormatLink

dispatcher = FormatToolDispatcher()
dispatcher.attach(FormatBold)
dispatcher.attach(FormatItalic)
dispatcher.attach(FormatQuote)
dispatcher.attach(FormatLink)
