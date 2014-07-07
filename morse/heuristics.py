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

from math import log
from datetime import datetime
from mappers import to_user_id, to_creation_timestamp

def interesting (posts):
    posters = map(to_user_id, posts)
    posters_count = len(set(posters))
    p = log(posters_count)

    timestamps = map(to_creation_timestamp, posts)
    timestamps.append(datetime.now())
    n = len(timestamps)
    deltasum = 0
    for i in xrange(1, n):
        delta = timestamps[i] - timestamp[i-1]
        fsum += delta.total_seconds()
    f = len(posts) / deltasum
    return p*f

