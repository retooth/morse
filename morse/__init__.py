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
from jinja2 import ChoiceLoader, FileSystemLoader
import os

app = Flask(__name__)
app.config.from_object('config')

from workers import make_celery
celery = make_celery(app)

# FIXME: for some reason FileSystemLoader
# doesn't like relative paths, so this is a
# workaround
path = os.getcwd() + "/morse/plugins"
app.jinja_loader = ChoiceLoader([ app.jinja_loader, FileSystemLoader(path)])

from morse.models import db
db.init_app(app)

import morse.views
import morse.routing
import morse.slots
from morse.views import login_manager
login_manager.init_app(app)

from plugins import *

from events import EventDispatcher
from tasks.ratings import rate_new_post, rate_edited_post
event_dispatcher = EventDispatcher()
event_dispatcher.connect_background_listener("post_id_created", rate_new_post)
event_dispatcher.connect_background_listener("post_id_edited", rate_edited_post)

