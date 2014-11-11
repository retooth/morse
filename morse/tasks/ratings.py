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
from . import db
from . import background
from ..models.ratings import PostRating
from ..models.discussion import Post
from ..api.dispatchers import PostRatingMethods

@background.task
def rate_new_post (post_id):

    with app.app_context():

        post = Post.query.get(post_id)

        post.calculate_ratings()
        db.session.commit()

        post.observe_ratings()

        topic = post.topic
        post_with_obsolete_rating = topic.next_post_with_obsolete_ratings
        if post_with_obsolete_rating is not None:
            post_with_obsolete_rating.unobserve_ratings()

        db.session.commit()

        topic.calculate_interesting_value()

        db.session.commit()
            
@background.task
def rate_edited_post (post_id):

    with app.app_context():

        post = Post.query.get(post_id)
    
        if post.ratings_observed:
            post.unobserve_ratings()
            post.calculate_ratings()
            post.observe_ratings()

        else:
            post.calculate_ratings()

        db.session.commit()

@background.task
def install_rating_methods ():

    with app.app_context():

        post_rating_methods = PostRatingMethods()
        identifiers = post_rating_methods.identifiers

        for identifier in identifiers:
            post_rating = PostRating.query.get(identifier)
            if post_rating is None:
                post_rating = PostRating(identifier)
                db.session.add(post_rating)

        db.session.commit()
