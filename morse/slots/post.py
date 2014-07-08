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
from ..protocols import ajax_triggered
from flask import request
from flask.ext.login import current_user
from ..models.discussion import Post
from ..wrappers import PostWrapper

@app.route('/posts/read', methods=['POST'])
@ajax_triggered
def read ():
    """ 
    marks posts as read. this function is called via ajax
    by the javascript function readVisiblePosts in topic.js
    """
    # just return success and do nothing
    # if user is guest
    if current_user.is_anonymous():
        return ""

    # please note: we don't check if the topic
    # is flagged as "following". this way posts
    # get flagged as "read" either way.    
    post_ids = request.json
    posts = []
    for post_id in post_ids:
        post = Post.query.get(post_id)
        if not post:
            continue
        posts.append(post)

    posts = map(PostWrapper, posts)
    for post in posts:
        post.read()

    return ""
