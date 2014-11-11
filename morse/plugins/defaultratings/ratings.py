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

from morse.api.ratings import PostRatingMethod

class Eloquence (PostRatingMethod):

    identifier = "default-rating-eloquence"
    name = "Eloquence"
    description = "Eloquence counts the number of unique words in a post."

    def determine_value (self, post):
        content = post.content
        words = content.split(" ")
        unique_words = list(set(words))
        eloquence = len(unique_words) * 100.0 / len(words)
        return eloquence
