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

import re
from . import app
from flask import render_template, request
from flask.ext.login import login_user 
from ..models import db
from ..models.core import User, GroupMember
from ..models.sorting import TopicSortingPreference
from ..models.filters import TopicFilter, PostFilter
from ..api.dispatchers import TopicFilterDispatcher, PostFilterDispatcher
from ..enum import GROUP_ID_REGISTERED

@app.route('/account/register' , methods=['GET','POST'])
def register():
    """ 
    Renders the register view on GET / registers a new user on POST
    :rtype: html
    """
    if request.method == 'GET':
        return render_template('account/register.html')
    
    username = request.form['username']
    password = request.form['password']
    email    = request.form['email']

    # TODO: mail authentication check

    # make sure, that username doesn't exist
    # in the database (we allow multiple accounts
    # for one email)
    user_exists = User.query.filter(User.username == username).first()
    if user_exists:
        return render_template('account/register.html', alert = 'userexists');

    pattern = "^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
    match = re.search(pattern, email)
    if not match:
        return render_template('account/register.html', alert = 'invalidemail');

    # all fine, create the new user
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()

    # insert the user in the registered group
    relationship = GroupMember(user.id, GROUP_ID_REGISTERED)
    db.session.add(relationship)

    # set default topic sorting preference
    topic_sorting_preference = TopicSortingPreference(user.id)
    db.session.add(topic_sorting_preference)

    # set default filter preferences
    topic_filter_dispatcher = TopicFilterDispatcher()
    for filter_blueprint in topic_filter_dispatcher:
        filter_entry = TopicFilter(user.id, filter_blueprint.id)
        db.session.add(filter_entry)

    post_filter_dispatcher = PostFilterDispatcher()
    for filter_blueprint in post_filter_dispatcher:
        filter_entry = PostFilter(user.id, filter_blueprint.id)
        db.session.add(filter_entry)

    db.session.commit()

    login_user(user)

    return render_template('account/redirect.html', alert = 'registered')
