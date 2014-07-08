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
from flask.ext.login import login_required
from ..rights import admin_rights_required
from ..models.core import Group

@app.route('/admin/groups', methods=['GET'])
@login_required
@admin_rights_required
def manage_groups ():
    """ 
    Renders the group management view
    :rtype: html
    """
    groups = Group.query.all()
    return render_template('admin/groups.html', groups = groups)
