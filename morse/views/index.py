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
from flask.ext.login import current_user
from flask import render_template
from ..rights import check_ban, possibly_banned 
from ..models.core import Board


@app.route('/')
@possibly_banned
def index():
    """ 
    Renders the index view
    :rtype: html
    """
    check_ban()
    boards = Board.query.all()
    boards = filter(current_user.may_read, boards)
    return render_template('index.html', boards = boards)
