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

from . import app
from flask import request
from flask.ext.login import login_required
from ..protocols import ajax_triggered
from ..api.dispatchers import TopicFilterDispatcher, PostFilterDispatcher

@app.route('/filter/topics', methods=['POST'])
@login_required
@ajax_triggered
def update_topic_filters ():
    """ 
    updates topic filters for current user
    """
    dispatcher = TopicFilterDispatcher()
    for status in request.json["filterStatus"]:
        string_identifier, active = status
        for filt in dispatcher:
            if string_identifier == filt.string_identifier:
                filt.active = active
                break
    return ""          

@app.route('/filter/posts', methods=['POST'])
@login_required
@ajax_triggered
def update_post_filters ():
    """ 
    updates post filters for current user
    """
    dispatcher = PostFilterDispatcher()
    for status in request.json["filterStatus"]:
        string_identifier, active = status
        for filt in dispatcher:
            if string_identifier == filt.string_identifier:
                filt.active = active
                break
    return ""
