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
from ..api.dispatchers import TopicFilterDispatcher

@app.route('/board/<board_str>')
@possibly_banned
def board(board_str):
    """ 
    Renders the board view for board_id
    :rtype: html
    """
    board_id = int(board_str.split("-")[0])
    check_ban(board_id)

    board  = Board.query.filter(Board.id == board_id).first()
    if not board:
        return render_template('4xx/404-default'), 404

    if not current_user.may_read(board):
        return render_template('4xx/403-default.html'), 403

    board  = Board.query.filter(Board.id == board_id).first()
    topic_filter_dispatcher = TopicFilterDispatcher()
    return render_template('board.html', board = board, topic_filter_dispatcher = topic_filter_dispatcher)
