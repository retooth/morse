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
from flask.ext.login import current_user, login_required
from ..rights import possibly_banned, check_ban
from ..models.account import UserWebsite

def hyperlink (website):
    """ mapping function (see below) """
    return website.hyperlink

@app.route('/account/settings')
@login_required
@possibly_banned
def settings():
    """ 
    Renders the settings view
    :rtype: html
    """
    check_ban()

    websites = UserWebsite.query.filter(UserWebsite.user_id == current_user.id).all()
    if not websites:
        websites = [""]
    else:
        websites = map(hyperlink, websites)

    bio = current_user.bio
    email = current_user.email

    return render_template('account/settings.html', \
                            websites = websites, bio = bio, email = email)
