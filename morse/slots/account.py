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
from flask.ext.login import login_required, current_user
from flask import request
from ..protocols import ajax_triggered
from ..rights import possibly_banned, check_ban
from ..models import db
from ..models.core import User
from ..models.account import UserWebsite

@app.route('/account/update-info', methods=['POST'])
@login_required
@possibly_banned
@ajax_triggered
def update_info ():
    """
    Updates bio/websites of user. Is called by the javascript
    event callback of #updateinfo
    """
    check_ban()

    info = request.json
    user = User.query.get(current_user.id)
    user.bio = info["bio"]

    websites = UserWebsite.query.filter(UserWebsite.user_id == current_user.id).all()
    # it's easier to remove and redo them
    # than to check which has changed and
    # which is new
    for website in websites:
        db.session.delete(website)

    # commit early, so ids are free again
    db.session.commit()

    for website in info["websites"]:
        w = UserWebsite(current_user, website)
        db.session.add(w)

    db.session.commit()
    return ""

@app.route('/account/update', methods=['POST'])
@login_required
@possibly_banned
@ajax_triggered
def update_account ():
    """
    Updates email/password of user. Is called by the javascript
    event callback of #updateaccount
    """
    check_ban()

    oldpassword = request.json["oldpassword"]
    if not current_user.has_password(oldpassword):
        return "wrongpassword", 403

    newpassword = request.json["newpassword"]
    if newpassword:
        current_user.password = newpassword

    current_user.email = request.json["newemail"]
    db.session.commit()
    return ""
