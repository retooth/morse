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
from flask import request, jsonify
from ..models.core import User
from ..protocols import ajax_triggered

@app.route('/search/users.json', methods=['GET'])
@ajax_triggered
def get_users ():
    """ 
    Gets a list of users matching GET 
    parameter pattern.
    :rtype: json
    """
    pattern = request.args.get('pattern')
    if pattern:
        users = User.query.filter(User.username.ilike('%' + pattern + '%')).all()
    else:
        users = User.query.all()

    userlist = []
    for u in users:
        userlist.append([u.id, u.username])

    return jsonify(users = userlist)
