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

from morse.models.discussion import Post, ReadPost
from morse.api.filters import PostItemFilter
from flask.ext.login import current_user
from sqlalchemy import not_

class UnreadPostFilter (PostItemFilter):

    id = 1
    string_identifier = "filter-option-unread"
    template = "postfilters/templates/unread.html"

    def filter (self, query):
        read_post_ids_generator = ReadPost.query.filter(ReadPost.user_id == current_user.id).values(ReadPost.post_id)
        read_post_ids = [oneple[0] for oneple in read_post_ids_generator]
        query = query.filter(not_(Post.id.in_(read_post_ids)))
        return query
