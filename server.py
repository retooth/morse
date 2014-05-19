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

# Conventions in this file:
#
# database_attribute
# function_name
# ClassName
# objectattribute
# object_method

from flask import render_template, url_for, request, g, jsonify, flash, redirect
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from contextlib import closing
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func, not_
from exceptions import *
from flask import Flask
from hashlib import md5, sha512
from urllib import urlencode
from urllib2 import urlopen, HTTPError
from collections import defaultdict

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

GROUP_ID_ADMIN = 1
GROUP_ID_MODERATORS = 2
GROUP_ID_REGISTERED = 3
GROUP_ID_GUESTS = 4

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def logged_in():
    # this is a strange workaround
    if not "id" in dir(current_user):
        return False
    return True
        
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    username = request.form['username']
    password = request.form['password']
    email    = request.form['email']

    # TODO: mail authentication check
    # TODO: check, if user exists
    user = User(username, password, email)
    db.session.add(user)
    db.session.commit()

    relationship = GroupMember(user.id, GROUP_ID_REGISTERED)
    db.session.add(relationship)
    db.session.commit()

    flash('User successfully registered')
    return redirect(url_for('login'))
 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = sha512(request.form['password']).hexdigest()
    registered_user = User.query.filter(User.username.like(username), User.password.like(password)).first()
    if not registered_user:
        flash('Username or Password is invalid' , 'error') #FIXME
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index')) 

class User (db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String)
    bio = db.Column(db.String(500), default="")

    def __init__ (self, username, password, email):
        self.username = username
        self.password = sha512(password).hexdigest();
        self.email = email

    @property
    def profileimage (self):
        email = self.email
        default_url = "/static/default.png"
        size = 64
        gravatar_url = "http://www.gravatar.com/avatar/" + md5(email.lower()).hexdigest() + "?"
        gravatar_url += urlencode({'d': '404', 's':str(size)})
        try:
            connection = urlopen(gravatar_url)
            if ( connection.getcode() == 404 ):
                url = default_url
            else:
                url = gravatar_url
            connection.close()
        except HTTPError, e:
            url = default_url
        return url

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    @property
    def maystructure (self):
        relations = GroupMember.query.filter(GroupMember.user_id.like(self.id)).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_structure:
                return True
                break
        return False

    @property
    def mayedit ():
        relations = GroupMember.query.filter(GroupMember.user_id.like(self.id)).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_edit:
                return True
                break
        return False

    @property
    def maydelete ():
        relations = GroupMember.query.filter(GroupMember.user_id.like(self.id)).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_delete:
                return True
                break
        return False

    @property
    def mayclose ():
        relations = GroupMember.query.filter(GroupMember.user_id.like(user_id)).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_close:
                return True
                break
        return False

class AlphabeticUserList (object):

    def __init__ (self):
        users = User.query.all()
        self.sortedusers = defaultdict(list)
        for user in users:
            firstletter = user.username[0]
            self.sortedusers[firstletter].append(user)

    def __getitem__ (self, letter):
        return self.sortedusers[letter] 

    @property
    def firstletters (self):
        return self.sortedusers.keys()    


class UserWebsite (db.Model):
    __tablename__ = "userwebsites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    hyperlink = db.Column(db.String(500))

    def __init__ (self, user, hyperlink):
        self.user_id = user.id
        self.hyperlink = hyperlink

def groupmode_to_group (groupmode):
    """ maps a groupmode relationship to its group object """
    return Group.query.get(groupmode.group_id)

def DummyBoard ():
    board = Board()
    board.id = 0
    return board

class Board (db.Model):
    __tablename__ = "boards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __init__ (self, title="", description=""):
        self.title = title
        self.description = description

    @property
    def ignorantgroups (self):
        """ 
        returns groups that relate to this 
        board with no right flag at all 
        :rtype [Group]
        """
        relationships = GroupMode.query.filter(GroupMode.board_id.like(self.id), \
                                               GroupMode.v.like(0), \
                                               GroupMode.r.like(0), \
                                               GroupMode.w.like(0)).all()
        return map(groupmode_to_group, relationships)

    @property
    def knowonlygroups (self):
        """ 
        returns groups that relate to this 
        board with only a (v)isible flag 
        :rtype [Group]
        """
        relationships = GroupMode.query.filter(GroupMode.board_id.like(self.id), \
                                               GroupMode.v.like(1), \
                                               GroupMode.r.like(0), \
                                               GroupMode.w.like(0)).all()
        return map(groupmode_to_group, relationships)
        groups = []

    @property
    def readonlygroups (self):
        """ 
        returns groups that relate to this 
        board with a (v)isible and (r)eadable flag 
        :rtype [Group]
        """
        relationships = GroupMode.query.filter(GroupMode.board_id.like(self.id), \
                                               GroupMode.v.like(1), \
                                               GroupMode.r.like(1), \
                                               GroupMode.w.like(0)).all()
        return map(groupmode_to_group, relationships)

    @property
    def postergroups (self):
        """ 
        returns groups that relate to this 
        board with a (v)isible, (r)eadable and (w)ritable flag 
        :rtype [Group]
        """
        relationships = GroupMode.query.filter(GroupMode.board_id.like(self.id), \
                                               GroupMode.v.like(1), \
                                               GroupMode.r.like(1), \
                                               GroupMode.w.like(1)).all()
        return map(groupmode_to_group, relationships)

class Group (db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))
    may_structure = db.Column(db.Boolean)
    may_edit = db.Column(db.Boolean)
    may_delete = db.Column(db.Boolean)
    may_close = db.Column(db.Boolean)

    def __init__ (self, name, description):
        self.name = name
        self.description = description
        self.may_structure = False
        self.may_edit = False
        self.may_delete = False
        self.may_close = False

    @property
    def members (self):
        members = []
        relations = GroupMember.query.filter(GroupMember.group_id.like(self.id)).all()        
        for r in relations:
            member = User.query.get(r.user_id)
            members.append(member)
        return members

class GroupMember (db.Model):
    __tablename__ = "groupmembers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def __init__ (self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id

class GroupMode (db.Model):
    __tablename__ = "groupmode"
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'), primary_key=True)
    r = db.Column(db.Boolean) # read
    w = db.Column(db.Boolean) # write
    v = db.Column(db.Boolean) # visible

    def __init__ (self, board_id, group_id = None, r = False, w = False, v = False):
        # TODO: warning group_id None is only for dummy purposes. saving will fail
        self.board_id = board_id
        self.group_id = group_id
        self.r = r
        self.w = w
        self.v = v

class Post (db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    content = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __init__ (self, user_id, content, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id
        self.content = content


class PostWrapper (object):

    # TODO: replace contextuser with global current_user
    def __init__ (self, contextuser, post):
        self.contextuser = contextuser
        self.post = post

    @property
    def user_id (self):
        return self.post.user_id

    @property
    def creator (self):
        return User.query.filter(User.id.like(self.user_id)).first()

    @property
    def id (self):
        return self.post.id
    
    @property
    def topic_id (self):
        return self.post.topic_id

    @property
    def content (self):
        return self.post.content

    @property
    def created_at (self):
        return self.post.created_at

    def _isfugitive (self):
        if self.post.id:
            return False
        return True

    @property
    def isfresh (self):
        if self._isfugitive():
            raise NotPersistentError("this property can only be used, when post is saved in the database")
        postread = PostRead.query.filter(PostRead.user_id.like(self.contextuser.id),\
                                         PostRead.post_id.like(self.post.id)).first()

        topic = Topic.query.filter(Topic.id.like(self.topic_id)).first()
        topic = wrap_topic(topic)
        if (postread is None) and (topic.followed):
            return True
        return False

    def read (self):
        if self._isfugitive():
            raise NotPersistentError("this method can only be used, when post is saved in the database")
        if self.isfresh:
            postread = PostRead(self.contextuser.id, self.id)
            db.session.add(postread)
            db.session.commit()

def wrap_post (post):
    return PostWrapper(current_user, post)

class Topic (db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    title = db.Column(db.String(100))

    def __init__ (self, board_id, title):
        self.board_id = board_id
        self.title = title

    @property
    def posts (self):    
        return Post.query.filter(Post.topic_id.like(self.id)).all()

class TopicFollow (db.Model):
    __tablename__ = "topicfollow"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key=True)

    def __init__ (self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id

class PostRead (db.Model):
    __tablename__ = "postread"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def __init__ (self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

class TopicWrapper (object):

    """ A wrapper class for Topic that adds user context to the model """
    
    def __init__ (self, user, topic):
        self.user  = user
        self.topic = topic

    def _getfollowrelation(self):
        return TopicFollow.query.filter(TopicFollow.user_id.like(self.user.id), \
                                        TopicFollow.topic_id.like(self.topic.id)).first()

    @property
    def followed (self):
        "Flag if topic is followed by user"
        relation = self._getfollowrelation()
        if relation:
            return True
        return False

    def follow (self):
        if not self.followed:
            topicfollow = TopicFollow(self.user.id, self.topic.id)
            db.session.add(topicfollow)
            db.session.commit()

    @property
    def posts (self):
        return map(wrap_post, self.topic.posts)

    @property
    def title (self):
        return self.topic.title

    @property
    def board_id (self):
        return self.topic.board_id

    @property
    def id (self):
        return self.topic.id

    def unfollow (self):
        relation = self._getfollowrelation()
        if relation:
            db.session.delete(relation)
            db.session.commit()

    @property
    def isfresh (self):
        if self.followed:
            onefresh = False
            for post in self.posts:
                onefresh |= post.isfresh
            return onefresh
        return False

def wrap_topic (topic):
    return TopicWrapper(current_user, topic)


def get_my_boards (get_only_ids=False):
    user_id = current_user.id
    relations = GroupMember.query.filter(GroupMember.user_id.like(user_id)).all() 
    # stack rights
    boardmodes = {}
    for r in relations:
        # exclude the 0 board id, because it is only used to save the groupmode default
        # (there is no corresponding board for it)
        modes = GroupMode.query.filter(GroupMode.group_id.like(r.group_id), not_(GroupMode.board_id.like(0))).all()
        for mode in modes:
            board_id = mode.board_id
            if not boardmodes.has_key(board_id):
                boardmodes[board_id] = GroupMode(board_id)
            boardmodes[ board_id ].r |= mode.r
            boardmodes[ board_id ].w |= mode.w
            boardmodes[ board_id ].v |= mode.v
    # filter invisible boards and split
    # into readable and writable boards
    readable_boards = []
    writable_boards = []
    for board_id, mode in boardmodes.iteritems():
        if mode.v:
            board = Board.query.filter(Board.id.like(board_id)).first()
            if mode.w:
                if get_only_ids: 
                    writable_boards.append(board.id)
                else:
                    writable_boards.append(board)
            if mode.r:
                if get_only_ids: 
                    readable_boards.append(board.id)
                else:
                    readable_boards.append(board)
    return readable_boards, writable_boards 



# Routes ################################################################# 

@app.route('/')
@login_required
def index():
    """ 
    Renders the index view
    :rtype: html
    """
    readable, writable = get_my_boards()
    return render_template('boards.html', boards=readable, logged_in = logged_in(), current_user = current_user)

@app.route('/board/<board_id>')
@login_required
def board(board_id):
    """ 
    Renders the board view for board_id
    :rtype: html
    """
    # TODO: order topics by timestamp
    readable, writable = get_my_boards( get_only_ids = True)
    if not int(board_id) in readable:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)
    board  = Board.query.filter(Board.id.like(board_id)).first()
    topics = Topic.query.filter(Topic.board_id.like(board_id)).all()
    topics = map(wrap_topic, topics)
    return render_template('board.html', board=board, topics=topics, logged_in = logged_in(), current_user = current_user)

@app.route('/admin')
@login_required
def admin():
    """ 
    Renders the admin view
    :rtype: html
    """
    if not current_user.maystructure:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)

    return render_template('admin.html', logged_in = logged_in(), current_user = current_user)

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

def GroupModes (board_id, group_ids, r, w, v):
    """ A GroupMode factory, that allows creating
    a list of GroupModes at once """
    groupmodes = []
    for group_id in group_ids:
        groupmode = GroupMode(board_id, group_id, r, w, v)
        groupmodes.append(groupmode)
    return groupmodes

def add_to_session (objectlist):
    """ adds a LIST of objects to session """
    for o in objectlist:
        db.session.add(o)

@app.route('/newboard', methods=["GET", "POST"])
@login_required
def newboard():
    """ 
    Renders the new board view
    (and does the backend logic)
    :rtype: html
    """
    if not current_user.maystructure:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)

    if request.method == 'GET':
        dummy = DummyBoard()
        return render_template('newboard.html', logged_in = logged_in(), current_user = current_user, board = dummy)

    title = request.form['boardtitle']
    description = request.form['boardescription']
    board = Board(title, description)
    db.session.add(board)
    db.session.commit()

    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    knowonly_ids = formlist_to_group_ids(request.form, "knowonly")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    # please note: GroupMode() != GroupModes()
    ignorant_modes = GroupModes(board.id, ignorant_ids, 0, 0, 0)
    knowonly_modes = GroupModes(board.id, knowonly_ids, 0, 0, 1)
    readonly_modes = GroupModes(board.id, readonly_ids, 1, 0, 1)
    poster_modes   = GroupModes(board.id, poster_ids, 1, 1, 1)

    add_to_session(ignorant_modes)
    add_to_session(knowonly_modes)
    add_to_session(readonly_modes)
    add_to_session(poster_modes)

    db.session.commit()

    return redirect(url_for('index'))

def update_groupmodes (board_id, group_ids, r, w, v):
    """ updates a list of groupmodes identified by board id
    and group ids """
    for group_id in group_ids:
        groupmode = GroupMode.query.filter(GroupMode.board_id.like(board_id), GroupMode.group_id.like(group_id)).first()
        groupmode.r = r
        groupmode.w = w
        groupmode.v = v

@app.route('/updateboard/<board_id>', methods=["GET", "POST"])
@login_required
def updateboard(board_id):
    """ 
    Renders the update board view
    (and does the backend logic)
    :rtype: html
    """
    if not current_user.maystructure:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)

    board = Board.query.get(board_id)
    if not board:
        return "", 400

    if request.method == 'GET':
        return render_template('updateboard.html', logged_in = logged_in(), current_user = current_user, board = board)

    board.title = request.form['boardtitle']
    board.description = request.form['boardescription']

    ignorant_ids = formlist_to_group_ids(request.form, "ignorant")
    knowonly_ids = formlist_to_group_ids(request.form, "knowonly")
    readonly_ids = formlist_to_group_ids(request.form, "readonly")
    poster_ids   = formlist_to_group_ids(request.form, "poster")

    update_groupmodes(board.id, ignorant_ids, 0, 0, 0)
    update_groupmodes(board.id, knowonly_ids, 0, 0, 1)
    update_groupmodes(board.id, readonly_ids, 1, 0, 1)
    update_groupmodes(board.id, poster_ids, 1, 1, 1)

    db.session.commit()

    return redirect(url_for('index'))

@app.route('/managegroups', methods=['GET', 'POST'])
def managegroups ():
    
    if not current_user.maystructure:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)

    if request.method == 'GET':
        groups = Group.query.all()
        userlist = AlphabeticUserList()
        return render_template('managegroups.html', logged_in = logged_in(), \
                                                    current_user = current_user, groups = groups, userlist = userlist)

    # TODO  

def groupmember_to_user_id (groupmember):
    return groupmember.user_id

def to_intlist (item):
    return int(item)

@app.route('/updategroup/<int:group_id>', methods=['POST'])
@login_required
def updategroup (group_id):
    """ 
    updates the group defined by group_id. this function is called
    by the javascript event handler for #updategroups in main.js
    :rtype: json 
    """
    if not current_user.maystructure:
        return "", 403

    groupmembers = GroupMember.query.filter(GroupMember.group_id.like(group_id)).all()
    old_user_ids = map(groupmember_to_user_id, groupmembers)
    new_user_ids = map(to_intlist,request.json)
    # make them sets and check the difference
    old_user_ids = set(old_user_ids)
    new_user_ids = set(new_user_ids)
    to_add = list( new_user_ids.difference(old_user_ids) )
    to_delete = list( old_user_ids.difference(new_user_ids) )

    print "add", to_add
    for id in to_add:
        g = GroupMember(id, group_id)
        db.session.add(g)

    print "delete", to_delete
    for id in to_delete:
        g = GroupMember.query.filter(GroupMember.user_id.like(id), GroupMember.group_id.like(group_id)).first()
        db.session.delete(g)

    db.session.commit()

    return jsonify(success=True)

def hyperlink (website):
    """ mapping function (see below) """
    return website.hyperlink

@app.route('/settings')
@login_required
def settings():
    """ 
    Renders the settings view
    :rtype: html
    """
    websites = UserWebsite.query.filter(UserWebsite.user_id.like(current_user.id)).all()
    if not websites:
        websites = [""]
    else:
        websites = map(hyperlink, websites)
    bio = current_user.bio
    email = current_user.email

    return render_template('settings.html', logged_in = logged_in(), current_user = current_user, websites=websites, bio=bio, email=email)

@app.route('/settings/updateinfo', methods=['POST'])
@login_required
def updateinfo ():
    """
    Updates bio/websites of user. Is called by the javascript
    event callback of #updateinfo
    :rtype: json 
    """
    info = request.json
    user = User.query.get(current_user.id)
    user.bio = info["bio"]

    websites = UserWebsite.query.filter(UserWebsite.user_id.like(current_user.id)).all()
    # it's easier to remove and redo them
    # than to check which has changed and
    # which is new
    for website in websites:
        db.session.delete(website)

    # commit early, so ids are free again
    db.session.commit()

    for website in info["websites"]:
        w = UserWebsite(current_user, website)
        db.session.add(w)

    db.session.commit()
    return jsonify(success=True)

@app.route('/settings/updateaccount', methods=['POST'])
@login_required
def updateaccount ():
    """
    Updates email/password of user. Is called by the javascript
    event callback of #updateaccount
    :rtype: json 
    """
    oldpassword = request.json["oldpassword"]
    if (current_user.password != sha512(oldpassword).hexdigest()):
        return jsonify(success=False)
    newpassword = request.json["newpassword"]
    if newpassword:
        current_user.password = sha512(newpassword).hexdigest()
    current_user.email = request.json["newemail"]
    db.session.commit()
    return jsonify(success=True)

@app.route('/board/<board_id>/starttopic', methods=['POST'])
@login_required
def starttopic (board_id):
    """ 
    Creates a new topic. Is called by the javascript event
    callback for #docreate
    :param board_id: board in which the new topic 
                     should be started
    :rtype: json 
    """
    readable, writable = get_my_boards( get_only_ids = True )
    if not int(board_id) in writable:
        return jsonify(success=False) 
    title = request.values["title"]
    text = request.values["text"]

    topic = Topic(board_id, title)
    db.session.add(topic)
    db.session.commit()

    wrapper = TopicWrapper(current_user, topic)
    wrapper.follow()

    post = Post(current_user.id, text, topic.id)
    db.session.add(post)
    db.session.commit()
    post = wrap_post(post)
    post.read()

    return jsonify(success=True, topicId=topic.id)


@app.route('/topic/<topic_id>/post', methods=['POST'])
@login_required
def post (topic_id):
    """ 
    Creates a new post. Is called by the javascript event
    callback for #dopost
    :param topic_id: topic to which the posts belongs
    :rtype: json 
    """
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()

    readable, writable = get_my_boards( get_only_ids = True)
    if not topic.board_id in writable:
        return jsonify(success=False)
 
    wrapper = TopicWrapper(current_user, topic)
    wrapper.follow()

    text = request.values["text"]
    post = Post(current_user.id, text, topic_id)
    db.session.add(post)
    db.session.commit()
    post = wrap_post(post)
    post.read()

    return jsonify(success=True, postId = post.id)


@app.route('/topic/<topic_id>', methods=['GET'])
@login_required
def showtopic (topic_id):
    """ 
    renders topic view
    :param topic_id: indicates topic view to render
    :rtype: html 
    """
    # TODO: page numbers
    # TODO: order by timestamp
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    topic = wrap_topic(topic)
    readable, writable = get_my_boards( get_only_ids = True)
    if not topic.board_id in readable:
        return render_template('accessdenied.html', logged_in = logged_in(), current_user = current_user)
    posts = map(wrap_post, topic.posts) 
    return render_template("topic.html", topic=topic, posts=posts, logged_in = logged_in(), current_user = current_user)

@app.route('/read', methods=['POST'])
@login_required
def read ():
    """ 
    marks posts as read. this function is called via ajax
    by the javascript function readVisiblePosts in main.js
    :rtype: json 
    """
    post_ids = request.json
    posts = []
    for post_id in post_ids:
        post = Post.query.filter(Post.id.like(post_id)).first()
        posts.append(post)
    posts = map(wrap_post, posts)
    for post in posts:
        post.read()
    return jsonify(success=True)

@app.route('/follow', methods=['POST'])
@login_required
def follow ():
    """ 
    follows a topic. this function is called via ajax
    by the click event handler for #followswitch in main.js
    :rtype: json 
    """
    topic_id = request.json
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    topic = wrap_topic(topic)
    topic.follow()
    return jsonify(success=True)

@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow ():
    """ 
    unfollows a topic. this function is called via ajax
    by the click event handler for #followswitch in main.js
    :rtype: json 
    """
    topic_id = request.json
    topic = Topic.query.filter(Topic.id.like(topic_id)).first()
    topic = wrap_topic(topic)
    topic.unfollow()
    return jsonify(success=True)

if __name__ == '__main__':
    db.create_all()
    app.debug = True
    app.run()
# vim: set expandtab:sw=4
