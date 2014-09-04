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
from ..validators import json_input, List, Integer, String
from ..protocols import ajax_triggered
from flask import request, jsonify
from flask.ext.login import current_user, login_required
from ..models.discussion import Post
from ..models import db
from ..wrappers import PostWrapper

@app.route('/posts/read', methods=['POST'])
@json_input({"postIDs": List(Integer())})
@ajax_triggered
def read_posts ():
    """ 
    marks posts as read. this function is called via ajax
    by the javascript function readVisiblePosts in topic.js
    """
    # just return success and do nothing
    # if user is guest
    if current_user.is_anonymous():
        return ""

    # please note: we don't check if the topic
    # is flagged as "followed". this way posts
    # get flagged as "read" either way.    
    post_ids = request.json["postIDs"]
    posts = []
    for post_id in post_ids:
        post = Post.query.get(post_id)
        if not post:
            continue
        post = PostWrapper(post)
        post.read()

    return ""

@app.route('/post/<int:post_id>/edit', methods=['POST'])
@login_required
@json_input({"editedContent": String()})
@ajax_triggered
def edit_post (post_id):
    """ 
    marks posts as read. this function is called via ajax
    by the javascript function readVisiblePosts in topic.js
    """
    post = Post.query.get(post_id)
    if not post:
        return "postnotfound", 404

    if not current_user.may_edit (post):
        return "forbidden", 403

    editedContent = request.json["editedContent"]
    post.content = editedContent

    if post.traits_observed:

        post.unobserve_traits()
        post.calculate_traits()
        db.session.commit()

        post.observe_traits()
        db.session.commit()

        post.topic.calculate_interesting_value()
        
    else:

        post.calculate_traits()
    
    db.session.commit()
    return ""

@app.route('/post/<int:post_id>/full-context.json', methods=['GET'])
@ajax_triggered
def full_context (post_id):
    """ 
    returns a json list of all posts connected to
    post with post_id
    """

    post = Post.query.get(post_id)
    if not post:
        return "postnotfound", 404

    post = PostWrapper(post)
    first_post_id = post.topic.first_post.id

    queue = [post_id]
    context = []
    while queue:
        current_post_id = queue.pop(0)
        if current_post_id in context:
            continue
        context.append(current_post_id)
        if not current_post_id == first_post_id:
            current_post = Post.query.get(current_post_id)
            reply_ids = [post.id for post in current_post.replies]
            reference_ids = [post.id for post in current_post.references]
            queue += (reply_ids + reference_ids)

    return jsonify(posts = context)
