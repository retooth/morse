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

GROUP_ID_ADMIN = 1
GROUP_ID_MODERATORS = 2
GROUP_ID_REGISTERED = 3
GROUP_ID_GUESTS = 4

USER_ID_GUESTS = 0

ALL_BOARDS = 0

# group modes save the default state
# with this dummy board id. default state
# is shown when creating a new board
DEFAULT_MODE_DUMMY_ID = 0

# sorting preferences
MOST_INTERESTING = 0
MOST_POSTS = 1
MOST_VIEWS = 2
MOST_USERS = 3
MOST_RECENT = 4

ASCENDING = 0
DESCENDING = 1

#filters
BOARD_FILTER_FAVORITED = 0
BOARD_FILTER_UNREAD = 1
BOARD_FILTER_NEW_TOPICS = 2
BOARD_FILTER_FOLLOWED = 3

TOPIC_FILTER_FAVORITED = 0
TOPIC_FILTER_UNREAD = 1
TOPIC_FILTER_FOLLOWED = 2

POST_FILTER_FAVORITED = 0
POST_FILTER_UNREAD = 1
