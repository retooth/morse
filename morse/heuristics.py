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
from wrappers import TopicWrapper

def interesting (topic):
    topic = TopicWrapper(topic)
    p = log(topic.posters_count)
    post_range = min(topic.post_count, 10)
    last_posts = topic[-post_range:]
    
    timestamps = [post.creation_timestamp for post in last_ten_posts]

    n = len(timestamps)
    deltasum = 0
    for i in xrange(1, n):
        delta = timestamps[i] - timestamp[i-1]
        deltasum += delta.total_seconds()
    try:
        f = len(last_posts) / deltasum
    except ArithmeticError:
        f = 1
    l = last_posts[-1].create_timestamp
    return p*f*l

