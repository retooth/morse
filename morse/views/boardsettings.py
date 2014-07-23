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
from flask import request, render_template, redirect, url_for
from flask.ext.login import login_required
from ..rights import admin_rights_required
from ..models import db
from ..models.core import Board, GroupMode 

def formlist_to_group_ids (form, prefix):
    i = 0
    group_ids = []
    while True:
        try:
            group_id = form[prefix + str(i)]
            group_ids.append(group_id)
            i += 1
        except KeyError:
            break
    return group_ids

def GroupModes (board_id, group_ids, may_read, may_post):
    """ A GroupMode factory, that allows creating
    a list of GroupModes at once """
    groupmodes = []
    for group_id in group_ids:
        groupmode = GroupMode(board_id, group_id, may_read, may_post)
        groupmodes.append(groupmode)
    return groupmodes

def add_to_session (objectlist):
    """ adds a LIST of objects to session """
    for o in objectlist:
        db.session.add(o)

def DummyBoard ():
    """ Generates a Board with Id 0 """
    board = Board()
    board.id = 0
    return board

@app.route('/admin/newboard', methods=["GET", "POST"])
@login_required
@admin_rights_required
def newboard():
    """ 
    Renders the new board view
    (and does the backend logic)
    :rtype: html
    """
    if request.method == 'GET':
        dummy = DummyBoard()
        return render_template('admin/newboard.html', board = dummy)

    title = request.form['boardtitle']
    description = request.form['boardescription']
    board = Board(title, description)
    db.session.add(board)
    db.session.commit()

    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    # please note: GroupMode() != GroupModes()
    ignorant_modes = GroupModes(board.id, ignorant_ids, False, False)
    readonly_modes = GroupModes(board.id, readonly_ids, True, False)
    poster_modes   = GroupModes(board.id, poster_ids, True, True)

    add_to_session(ignorant_modes)
    add_to_session(readonly_modes)
    add_to_session(poster_modes)

    db.session.commit()

    return redirect(url_for('index'))

def update_groupmodes (board_id, group_ids, may_read, may_post):
    """ updates a list of groupmodes identified by board id
    and group ids """
    for group_id in group_ids:
        groupmode = GroupMode.query.filter(GroupMode.board_id == board_id,\
                                           GroupMode.group_id == group_id).first()
        if not groupmode:
            continue

        groupmode.may_read = may_read
        groupmode.may_post = may_post

@app.route('/admin/updateboard/<board_id>', methods=["GET", "POST"])
@login_required
@admin_rights_required
def updateboard(board_id):
    """ 
    Renders the update board view
    (and does the backend logic)
    :rtype: html
    """
    board = Board.query.get(board_id)
    if not board:
        return "", 400

    if request.method == 'GET':
        return render_template('admin/updateboard.html', board = board)

    board.title = request.form['boardtitle']
    board.description = request.form['boardescription']
    for key in request.form:
        print key, request.form[key]
    
    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    update_groupmodes(board.id, ignorant_ids, False, False)
    update_groupmodes(board.id, readonly_ids, True, False)
    update_groupmodes(board.id, poster_ids, True, True)

    db.session.commit()

    return redirect(url_for('index'))
