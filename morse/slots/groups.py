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
from ..rights import admin_rights_required
from ..models import db
from ..protocols import ajax_triggered
from ..models.core import Board, Group, GroupMode, GroupMember
from ..enum import DEFAULT_MODE_DUMMY_ID

@app.route('/groups/adduser', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def add_user_to_group():
    """
    Adds new user to a group.
    """
    user_id = request.json["userID"]
    group_id = request.json["groupID"]
    # check if user is already in group
    already_in_group = GroupMember.query.filter(GroupMember.user_id == user_id,
                                                GroupMember.group_id == group_id).first()
    if already_in_group:
        return "alreadyingroup", 412

    rel = GroupMember(user_id, group_id)
    db.session.add(rel)
    db.session.commit()

    return ""

@app.route('/groups/removeuser', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def remove_user_from_group():
    """
    Removes a user from a group.
    """
    user_id = request.json["userID"]
    group_id = request.json["groupID"]
    # check if user is already in group
    rel = GroupMember.query.filter(GroupMember.user_id == user_id,
                                   GroupMember.group_id == group_id).first()
    if not rel:
        return "notingroup", 400

    db.session.delete(rel)
    db.session.commit()

    return ""

@app.route('/groups/changelabel', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def change_group_label():
    """
    changes the label of a group.
    """
    group_id = request.json["groupID"]
    label_id = request.json["labelID"]
    # check if user is already in group
    group = Group.query.get(group_id)
    if not group:
        return "groupnotfound", 404

    group.label = label_id
    db.session.commit()

    return ""

@app.route('/groups/updaterights', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def update_group_rights ():
    """ 
    updates the group rights defined by groupID. this function is 
    called by a javascript event handler, that listens to checkbox 
    changes in admin/groups.js.
    """
    group_id = request.json["groupID"]
    group = Group.query.get(group_id)
    if not group:
        return "groupnotfound", 404

    group.may_edit = request.json["mayEdit"]
    group.may_close = request.json["mayClose"]
    group.may_stick = request.json["mayStick"]
    db.session.commit()

    return ""

@app.route('/groups/create', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def create_group ():
    """ 
    creates a new group and returns its id as json
    this function is called by the javascript 
    event handler for #newgroupname in admin/groups.js.
    """
    name = request.json['name']

    #check if group already exists
    already_exists = Group.query.filter(Group.name == name).first()
    if already_exists:
        return "groupexists", 412

    group = Group(name)
    db.session.add(group)
    db.session.commit()

    boards = Board.query.all()
    for board in boards:
        mode = GroupMode(board.id, group.id)
        db.session.add(mode)

    mode_default = GroupMode(DEFAULT_MODE_DUMMY_ID, group.id)
    db.session.add(mode_default)

    db.session.commit()

    return jsonify(newGroupID = group.id, name = name)

@app.route('/groups/delete', methods=['POST'])
@login_required
@admin_rights_required
@ajax_triggered
def delete_group ():
    """ 
    deletes a group and all its dependencies
    this function is called by the javascript 
    event handler for .deletegroup in admin/groups.js.
    """
    group_id = request.json['groupID']
    group = Group.query.get(group_id)
    if not group:
       return "nosuchgroup", 400

    members = GroupMember.query.filter(GroupMember.group_id == group_id).all()
    for m in members:
        db.session.delete(m)
    db.session.commit()

    modes = GroupMode.query.filter(GroupMode.group_id == group_id).all()
    for m in modes:
        db.session.delete(m)
    db.session.commit()

    db.session.delete(group)

    db.session.commit()
    return ""
