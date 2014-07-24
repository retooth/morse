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
from flask import render_template
from flask.ext.login import current_user
from ..rights import possibly_banned, check_ban
from ..models import db
from ..models.discussion import Topic
from ..wrappers import TopicWrapper
from ..api.dispatchers import PostFilterDispatcher, FormatToolDispatcher

@app.route('/topic/<topic_str>', methods=['GET'])
@possibly_banned
def topic (topic_str):
    """ 
    renders topic view
    :param topic_id: indicates topic view to render
    :rtype: html 
    """
    topic_id = int(topic_str.split("-")[0])
    topic = Topic.query.get(topic_id)
    if not topic:
       return "nosuchtopic", 400

    check_ban(topic.board_id)

    topic = TopicWrapper(topic)

    if not current_user.may_read(topic.board):
        return render_template('4xx/403-default.html'), 403

    topic.view_count += 1
    db.session.commit()

    post_filter_dispatcher = PostFilterDispatcher()
    format_tool_dispatcher = FormatToolDispatcher()

    return render_template("topic.html", topic = topic, 
                            post_filter_dispatcher = post_filter_dispatcher,
                            format_tool_dispatcher = format_tool_dispatcher)
