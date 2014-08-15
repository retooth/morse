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
from flask.ext.login import login_required
from ..validators import json_input, IPRange, String, Integer, List 
from ..rights import certain_rights_required
from ..models import db
from ..protocols import ajax_triggered
from ..models.bans import IPBan, IPBannedOn
from ..enum import DEFAULT_MODE_DUMMY_ID

@app.route('/ip-bans/new', methods=['POST'])
@login_required
@certain_rights_required(may_ban=True)
@json_input({"IPRange": IPRange(), "reason": String(), 
             "affectedBoards": List(Integer())},
            {"duration": Integer()})
@ajax_triggered
def issue_ip_ban():
    """
    Adds new ip rule to the ban table.
    """

    ip_range = request.json["IPRange"]
    reason = request.json["reason"]
    affected_boards = request.json["affectedBoards"]

    if not 'duration' in request.json:
        ban = IPBan(ip_range, reason)
        db.session.add(ban)
        db.session.commit()
    else:
        duration = request.json["duration"]
        ban = IPBan(ip_range, reason, duration)
        db.session.add(ban)
        db.session.commit()

    for board_id in affected_boards:
        banned_board = IPBannedOn(board_id, ban.id)
        db.session.add(banned_board)

    db.session.commit()
    
    return ""

@app.route('/ip-bans/<int:ban_id>/update', methods=['POST'])
@login_required
@certain_rights_required(may_ban=True)
@json_input({"IPRange": IPRange(), "reason": String(), 
             "affectedBoards": List(Integer())},
            {"duration": Integer()})
@ajax_triggered
def update_ip_ban(ban_id):
    
    ban = IPBan.query.get(ban_id)
    if not ban:
        return "bannotfound", 404

    ip_range = request.json["IPRange"]
    reason = request.json["reason"]
    affected_boards = request.json["affectedBoards"]

    ban.ip_range = ip_range
    ban.reason = reason

    if 'duration' in request.json:
        ban.duration_in_days = request.json["duration"]
    else:
        ban.duration_in_days = None

    old_affected_boards = IPBannedOn.query.filter(IPBannedOn.ban_id == ban.id).all()
    for banned_board in old_affected_boards:
        db.session.delete(banned_board)

    for board_id in affected_boards:
        banned_board = IPBannedOn(board_id, ban.id)
        db.session.add(banned_board)

    db.session.commit()
    return "", 200
