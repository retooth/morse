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
from flask import render_template, request, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user
from ..models.core import User, Guest

# Integration into flask login extension
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.anonymous_user = Guest

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/account/login',methods=['GET','POST'])
def login():
    """ 
    Renders the login view on GET / logs a user in on POST
    :rtype: html
    """
    if request.method == 'GET':
        return render_template('account/login.html')

    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter(User.username == username).first()

    if not registered_user or not registered_user.has_password(password):
        return render_template('account/login.html', alert = 'loginfailed')

    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/account/logout')
def logout():
    """ 
    Logs out and redirects to index
    :rtype: html
    """
    logout_user()
    return redirect(url_for('index')) 
