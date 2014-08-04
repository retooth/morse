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
from ..rights import certain_rights_required
from ..models import db
from ..protocols import ajax_triggered
from ..models.bans import LimitedIPBan, PermaIPBan, LimitedIPBannedOn, PermaIPBannedOn
from ..enum import DEFAULT_MODE_DUMMY_ID

@app.route('/ip-bans/new', methods=['POST'])
@login_required
@certain_rights_required(may_ban=True)
@ajax_triggered
def issue_ip_ban():
    """
    Adds new ip rule to the ban table.
    """

    ip_range = request.json["IPRange"]
    reason = request.json["reason"]
    affected_boards = request.json["affectedBoards"]

    if not 'duration' in request.json:
        ban = PermaIPBan(ip_range, reason)
        db.session.add(ban)
        db.session.commit()
        for board_id in affected_boards:
            banned_board = PermaIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)
    else:
        duration = request.json["duration"]
        ban = LimitedIPBan(ip_range, reason, duration)
        db.session.add(ban)
        db.session.commit()
        for board_id in affected_boards:
            banned_board = LimitedIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)

    db.session.commit()
    
    return ""


@app.route('/ip-bans/permanent/<int:ban_id>/update', methods=['POST'])
@login_required
@certain_rights_required(may_ban=True)
@ajax_triggered
def update_perma_ip_ban(ban_id):
    
    ban = PermaIPBan.query.get(ban_id)
    if not ban:
        return "bannotfound", 404

    ip_range = request.json["IPRange"]
    reason = request.json["reason"]
    affected_boards = request.json["affectedBoards"]

    old_affected_boards = PermaIPBannedOn.query.filter(PermaIPBannedOn.ban_id == ban.id).all()
    for banned_board in old_affected_boards:
        db.session.delete(banned_board)

    if 'duration' in request.json:
        db.session.delete(ban)
        ban = LimitedIPBan(ip_range, reason, duration)
        db.session.add(ban)
        db.session.commit()
        for board_id in affected_boards:
            banned_board = LimitedIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)

    else:
        ban._ip_range = ip_range
        ban.reason = reason
        db.session.commit()
        for board_id in affected_boards:
            banned_board = PermaIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)

    db.session.commit()
    return "", 200
    
@app.route('/ip-bans/limited/<int:ban_id>/update', methods=['POST'])
@login_required
@certain_rights_required(may_ban=True)
@ajax_triggered
def update_limited_ip_ban(ban_id):
    
    ban = LimitedIPBan.query.get(ban_id)
    if not ban:
        return "bannotfound", 404

    ip_range = request.json["IPRange"]
    reason = request.json["reason"]
    affected_boards = request.json["affectedBoards"]

    old_affected_boards = LimitedIPBannedOn.query.filter(LimitedIPBannedOn.ban_id == ban.id).all()
    for banned_board in old_affected_boards:
        db.session.delete(banned_board)

    if not 'duration' in request.json:
        db.session.delete(ban)
        ban = PermaIPBan(ip_range, reason)
        db.session.add(ban)
        db.session.commit()
        for board_id in affected_boards:
            banned_board = PermaIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)

    else:
        ban._ip_range = ip_range
        ban.reason = reason
        
        ban.duration_in_days = request.json["duration"]

        db.session.commit()
        for board_id in affected_boards:
            banned_board = LimitedIPBannedOn(board_id, ban.id)
            db.session.add(banned_board)

    db.session.commit()
    return "", 200
    
