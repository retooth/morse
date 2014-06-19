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

from enum import GROUP_ID_GUESTS, USER_ID_GUESTS
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import not_
from flask.ext.login import current_user
from sqlalchemy import func
from hashlib import md5, sha512
from urllib import urlencode
from urllib2 import urlopen, HTTPError
from iptools import IpRange

db = SQLAlchemy()

class User (db.Model):
    
    """ User is the database representation of a registered user.
    It also implements the interface for the Flask login
    extension. """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    _email = db.Column(db.String(100))
    _password = db.Column(db.String)
    bio = db.Column(db.String(500), default="")

    def __init__ (self, username, password, email):
        """ password should be cleartext (gets hashed automatically) """
        self.username = username
        self.password = password
        self.email = email

    def _getpassword (self):
        return self._password

    def _setpassword (self, password):
        self._password = sha512(password).hexdigest()

    password = property(_getpassword, _setpassword, \
                        "when setting use cleartext (gets hashed automatically)")

    def has_password (self, password):
        """ returns boolean if passwords match """
        return self._password == sha512(password).hexdigest()

    def _getmail (self):
        return self._email

    def _setmail (self, addr):
        # TODO: do server check on email
        self._email = addr.lower()

    email = property(_getmail, _setmail, \
                     "Proxy attribute for _email. Please use this and don't set _email directly")

    @property
    def profileimage (self):
        """ Gravatar URL for submitted email address """
        email = self.email
        size = 64
        gravatar_url = "http://www.gravatar.com/avatar/" + \
                        md5(email).hexdigest() + "?" + \
                        urlencode({ 'd' : '404', 's' : str(size) })
        default_url = "/static/default.png"
        try:
            connection = urlopen(gravatar_url)
            if connection.getcode() == 404:
                url = default_url
            else:
                url = gravatar_url
            connection.close()
        except HTTPError:
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
    def may_structure (self):
        """ signifies if user may manipulate groups and create/delete/deactivate boards.
        This property is read only. To change it for a specific user, move him/her
        to the admin group or create a group with the may_structure flag """
        relations = GroupMember.query.filter(GroupMember.user_id == self.id).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_structure:
                return True
                break
        return False

    @property
    def may_edit (self):
        """ signifies if user may edit *ALL* posts. This is typically a moderator's right.
        This property is read only. To change it for a specific user, move him/her
        to the moderator / admin group or create a group with the may_edit flag """
        relations = GroupMember.query.filter(GroupMember.user_id == self.id).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_edit:
                return True
                break
        return False

    @property
    def may_close (self):
        """ signifies if user may close threads. This is typically a moderator's right.
        This property is read only. To change it for a specific user, move him/her
        to the moderator / admin group or create a group with the may_close flag """
        relations = GroupMember.query.filter(GroupMember.user_id == self.id).all() 
        for r in relations:
            group = Group.query.get(r.group_id)
            if group.may_close:
                return True
                break
        return False

    def may_post_in (self, board):
        """ signifies if a user may post in a specific board. This is used in
        in templates to decide, if the post dialog is shown"""
        readable, writable, visible = get_my_boards(user = self, get_only_ids = True)
        return board.id in writable

class UserWebsite (db.Model):
    __tablename__ = "userwebsites"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    hyperlink = db.Column(db.String(500))

    def __init__ (self, user, hyperlink):
        self.user_id = user.id
        self.hyperlink = hyperlink

class Ban (db.Model):
    """ abstract model for bans """
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String)

class IPBan (Ban):
    """ abstract model for IP bans """
    __abstract__ = True
    _ip_range = db.Column(db.String)

    @property
    def ip_range (self):
        """ use this property instead of _ip_range. it provides a
        iptools.IpRange object instead of a simple string, which
        means you can perform containment operations (e.g.
        "my_ip in ban.ip_range" and the like) """
        return IpRange(self._ip_range)

class PermaIPBan (IPBan):
    """ Use this, if you want to create a permanent IP ban """
    __tablename__ = "permanent_ipbans"
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, ip_range, board_id, reason):
        self._ip_range = ip_range
        self.board_id = board_id
        self.reason = reason

class LimitedIPBan (IPBan):
    """ Use this, if you want to create a limited IP ban """
    __tablename__ = "limited_ipbans"
    expires = db.Column(db.DateTime)
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, ip_range, board_id, reason, expires):
        self._ip_range = ip_range
        self.board_id = board_id
        self.reason = reason
        self.expires = expires

class PermaUserBan (Ban):
    """ Use this, if you want to create a permanent user ban """
    __tablename__ = "permanent_userbans"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, user_id, board_id, reason):
        self.user_id = user_id
        self.board_id = board_id
        self.reason = reason

class LimitedUserBan (Ban):
    """ Use this, if you want to create a limited user ban """
    __tablename__ = "limited_userbans"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    board_id = db.Column(db.ForeignKey("boards.id"))

    def __init__ (self, user_id, board_id, reason, expires):
        self.user_id = user_id
        self.board_id = board_id
        self.reason = reason
        self.expires = expires

def groupmode_to_group (groupmode):
    """ maps a groupmode relationship to its group object """
    return Group.query.get(groupmode.group_id)

def get_my_boards (user = current_user, get_only_ids = False):
    """ returns a triplet (visible, readable, writable) with each element
    being a list of boards. the triplet is a representation of the current
    user's rights on the community """
    if user.is_anonymous():
        dummy = GroupMember(USER_ID_GUESTS, GROUP_ID_GUESTS)
        relations = [dummy]
    else:
        user_id = user.id
        relations = GroupMember.query.filter(GroupMember.user_id == user_id).all() 

    # stack rights
    boardmodes = {}
    for r in relations:
        # exclude the 0 board id, because it is only used to save the groupmode default
        # (there is no corresponding board for it)
        modes = GroupMode.query.filter(GroupMode.group_id == r.group_id, not_(GroupMode.board_id == 0)).all()
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
    visible_boards  = []
    writable_boards = []
    for board_id, mode in boardmodes.iteritems():
        if mode.v:
            board = Board.query.filter(Board.id == board_id).first()
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
            if get_only_ids:
                visible_boards.append(board.id)
            else:
                visible_boards.append(board)
    return visible_boards, readable_boards, writable_boards 

def make_url_compatible (string):
    """removes all characters except alphanumeric ones and
    whitespaces, which are substituted with underscores"""
    allowed = []
    for char in string:
        if char.isalnum() or char == " ":
            allowed.append(char)
    allowed = ''.join(allowed)
    return allowed.replace(" ", "_")

class Board (db.Model):
    __tablename__ = "boards"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __init__ (self, title="", description=""):
        self.title = title
        self.description = description

    @property
    def seostring (self):
        string = str(self.id) + "-" + make_url_compatible(self.title) 
        return string

    @property
    def ignorantgroups (self):
        """ returns groups that relate to this 
        board with no right flag at all 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.v == False, \
                                               GroupMode.r == False, \
                                               GroupMode.w == False).all()
        return map(groupmode_to_group, relationships)

    @property
    def knowonlygroups (self):
        """ returns groups that relate to this 
        board with only a (v)isible flag 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.v == True, \
                                               GroupMode.r == False, \
                                               GroupMode.w == False).all()
        return map(groupmode_to_group, relationships)
        groups = []

    @property
    def readonlygroups (self):
        """ returns groups that relate to this 
        board with a (v)isible and (r)eadable flag 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.v == True, \
                                               GroupMode.r == True, \
                                               GroupMode.w == False).all()
        return map(groupmode_to_group, relationships)

    @property
    def postergroups (self):
        """ returns groups that relate to this 
        board with a (v)isible, (r)eadable and (w)ritable flag 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.v == True, \
                                               GroupMode.r == True, \
                                               GroupMode.w == True).all()
        return map(groupmode_to_group, relationships)

class Group (db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    may_structure = db.Column(db.Boolean)
    may_edit = db.Column(db.Boolean)
    may_close = db.Column(db.Boolean)
    may_stick = db.Column(db.Boolean)
    label = db.Column(db.Integer)

    def __init__ (self, name, may_structure = False, \
                  may_edit = False, may_close = False, may_stick = False, label=0):
        self.name = name
        self.may_structure = may_structure
        self.may_edit = may_edit
        self.may_close = may_close
        self.may_stick = may_stick
        self.label = label

    @property
    def members (self):
        """ all members of this group
        :rtype [User] """
        members = []
        relations = GroupMember.query.filter(GroupMember.group_id == self.id).all()        
        for r in relations:
            member = User.query.get(r.user_id)
            members.append(member)
        return members

    def has_label (self, label):
        return self.label == label

class GroupMember (db.Model):

    """ A Many-To-Many Relationship of Users and Groups """

    __tablename__ = "groupmembers"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    def __init__ (self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id

class GroupMode (db.Model):

    """ A relation that connects groups with boards and 
    defines their rights in them. 

    WARNING: You can create nonsensical right combinations,
    such as writable, but not readable, etc. If you do this
    you *cannot* edit the groups in the graphical interface,
    because it filters the entries into 4 distinct groups
    1. no rights     (r=0,w=0,v=0)
    2. visible only  (r=0,w=0,v=1)
    3. readable only (r=1,w=0,v=1)
    4. all rights    (r=1,w=1,v=1)
    """

    __tablename__ = "groupmode"
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    board_id = db.Column(db.Integer, primary_key=True) # no foreign key here, because
                                                       # of 0-dummy value
    r = db.Column(db.Boolean) # read
    w = db.Column(db.Boolean) # write
    v = db.Column(db.Boolean) # visible

    def __init__ (self, board_id, group_id = None, r = False, w = False, v = False):
        # if you wonder, why group_id has default None
        # look at the get_my_boards function
        self.board_id = board_id
        self.group_id = group_id
        self.r = r
        self.w = w
        self.v = v

class Post (db.Model):

    """ Model for post entries. Links to user and topic and provides
    metadata (such as creation time and remote address of the poster)
    """

    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    content = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=func.now())
    remote_addr = db.Column(db.String)

    def __init__ (self, user_id, content, topic_id, remote_addr):
        self.user_id = user_id
        self.topic_id = topic_id
        self.content = content
        self.remote_addr = remote_addr

class Topic (db.Model):
    
    """ Model for topic entries. Saves title and links to board. It 
    provides also a sticky flag (that moderators can use to put
    the topic permanently on top)
    """

    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey('boards.id'))
    title = db.Column(db.String(100))
    closed = db.Column(db.Boolean)
    sticky = db.Column(db.Boolean)

    def __init__ (self, board_id, title):
        self.board_id = board_id
        self.title = title
        self.sticky = False
        self.closed = False

    @property
    def seostring (self):
        string = str(self.id) + "-" + make_url_compatible(self.title) 
        return string

    @property
    def posts (self):
        """ Returns all posts of this topic :rtype [Post] """    
        return Post.query.filter(Post.topic_id == self.id).all()

class TopicFollow (db.Model):

    """ A many-to-many relation between users and topics. If relations exists
    the user with user_id follow the topic with topic_id. If not, not """

    __tablename__ = "topicfollow"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), primary_key=True)

    def __init__ (self, user_id, topic_id):
        self.user_id = user_id
        self.topic_id = topic_id

class PostRead (db.Model):

    """ A many-to-many relation between users and posts. If relations exists
    the user with user_id has read the post with topic_id. If not, not """

    __tablename__ = "postread"
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)

    def __init__ (self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id
