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

from . import db
# FIXME (global: replace mappers)
from ..mappers import to_filter_id
from enum import GROUP_ID_GUESTS
from sorting import TopicSortingPreference
from filters import TopicFilter, PostFilter
from flask.ext.login import AnonymousUserMixin
from hashlib import md5, sha512
from urllib import urlencode
from urllib2 import urlopen, HTTPError, URLError
from helpers import make_url_compatible

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
        size = 128
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
        except (HTTPError, URLError):
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
        """ signifies if a user may post in a specific board. """
        
        relations = GroupMember.query.filter(GroupMember.user_id == self.id).all() 
        for r in relations:
            mode = GroupMode.query.filter(GroupMode.group_id == r.group_id,
                                          GroupMode.board_id == board.id).first()
            if mode.may_post:
                return True
                break
        return False

    def may_read (self, board):
        """ signifies if a user may read a specific board. """
        
        relations = GroupMember.query.filter(GroupMember.user_id == self.id).all() 
        for r in relations:
            mode = GroupMode.query.filter(GroupMode.group_id == r.group_id,
                                          GroupMode.board_id == board.id).first()
            if mode.may_read:
                return True
                break
        return False

    @property
    def topic_sorting_preference (self):
        rel = TopicSortingPreference.query.get(self.id)
        return rel.preference_id

    @property
    def active_topic_filters(self):
        rel = TopicFilter.query.filter(TopicFilter.user_id == self.id, TopicFilter.active == True).all()
        filters = map(to_filter_id, rel)
        return filters

    @property
    def active_post_filters(self):
        rel = PostFilter.query.filter(PostFilter.user_id == self.id, PostFilter.active == True).all()
        filters = map(to_filter_id, rel)
        return filters

class Guest (AnonymousUserMixin):

    @property
    def id (self):
        return 0

    @property
    def active_topic_filters(self):
        return []

    @property
    def active_post_filters(self):
        return []

    def may_post_in (self, board):
        """ signifies if a user may post in a specific board. """
        
        mode = GroupMode.query.filter(GroupMode.group_id == GROUP_ID_GUESTS,
                                      GroupMode.board_id == board.id).first()
        return mode.may_post

    def may_read (self, board):
        """ signifies if a user may read a specific board. """
        
        mode = GroupMode.query.filter(GroupMode.group_id == GROUP_ID_GUESTS,
                                      GroupMode.board_id == board.id).first()
        return mode.may_read
 
def groupmode_to_group (groupmode):
    """ maps a groupmode relationship to its group object """
    return Group.query.get(groupmode.group_id)

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
                                               GroupMode.may_read == False, \
                                               GroupMode.may_post == False).all()
        return map(groupmode_to_group, relationships)

    @property
    def readonlygroups (self):
        """ returns groups that relate to this 
        board with a may_read flag 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.may_read == True, \
                                               GroupMode.may_post == False).all()
        return map(groupmode_to_group, relationships)

    @property
    def postergroups (self):
        """ returns groups that relate to this 
        board with a may_post flag 
        :rtype [Group] """
        relationships = GroupMode.query.filter(GroupMode.board_id == self.id, \
                                               GroupMode.may_read == True, \
                                               GroupMode.may_post == True).all()
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
    """

    __tablename__ = "groupmode"
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    board_id = db.Column(db.Integer, primary_key=True) # no foreign key here, because
                                                       # of 0-dummy value
    may_post = db.Column(db.Boolean)
    may_read = db.Column(db.Boolean)

    def __init__ (self, board_id, group_id, may_read = False, may_post = False):
        self.board_id = board_id
        self.group_id = group_id
        self.may_read = may_read
        self.may_post = may_post
