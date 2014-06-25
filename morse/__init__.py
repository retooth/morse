#!/usr/bin/python

#    This package is part of Morse.
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

from flask import Flask
app = Flask(__name__)
app.config.from_object('config')

from morse.models import db
db.init_app(app)

import morse.views
import morse.routing
import morse.slots
import morse.builders
from morse.views import login_manager
login_manager.init_app(app)
