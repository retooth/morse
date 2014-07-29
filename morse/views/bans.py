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
from ..rights import certain_rights_required 
from ..models.core import Board
from ..models.bans import PermaIPBan, LimitedIPBan
from ..wrappers import BoardWrapper

@app.route('/moderation/bans')
@certain_rights_required(may_ban=True)
def bans():
    """ 
    Renders the banned users view
    :rtype: html
    """
    limited_bans = LimitedIPBan.query.order_by(LimitedIPBan.expires.asc()).all()
    perma_bans = PermaIPBan.query.all()
    ip_bans = limited_bans + perma_bans

    boards = Board.query.all();
    return render_template('moderation/bans.html', ip_bans = ip_bans, boards = boards)