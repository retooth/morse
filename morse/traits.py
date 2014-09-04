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

from api.dispatchers import PostTraitDispatcher
from models.traits import PostTrait, PostTraitSum

""" 
this module implements inferface functions for traits, which are used 
in the slots package. it manages the backend logic of calculating
and caching different traits. this module is strongly connected
to the morse.interesting module, which uses the cache generated
in here.

for a more general introduction of what traits are check the 
docs of the morse.api.traits module
""" 

post_margin = 10

def calculateTraitValues (post, post_traits):

    """ calculates traits for a new post and adds the trait
    values to the corresponding cache sums. 

    !!! IMPORTANT: only use this for posts, that haven't already been 
    passed to this function. generally calculateTraitValues gets only invoked 
    at post creation time. every change made to a post after creation 
    has to be checked by recalculateTraitValues(). considerPost will throw
    no exception whatsoever if you do this wrong, but will silently
    generate a bunch of wrong values.
    """

    query = Post.query.order_by(Post.created_at)
    posts = query.limit(post_margin).all()

    if len(posts) == post_margin:
        # if we add a new post, one post falls out 
        # of the margin. this means we must substract 
        # its trait values from the sums
        overhanging_post = posts[0]
        for post_trait in PostTraitDispatcher():
            # skip everything if trait is not
            # active
            if not post_trait.is_relevant:
                continue
            # get trait value
            query = PostTraitValue.query.filter(PostTraitValue.post_id == overhanging_post.id)
            query = query.filter(PostTraitValue.trait_id == post_trait.id)
            rel = query.first()
            value_for_subtraction = rel.value
            # subtract it
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == post.topic.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.id).first()
            sum_rel.value -= value_for_substraction
            
        
    for post_trait in PostTraitDispatcher():
        if not post_trait.is_relevant:
            continue
        # calculate trait values of new post
        value = post_trait.determine_value(post)
        new_value_rel = PostTraitValue(post.id, post_trait.id, value) 
        db.session.add(new_value_rel)
        # add to sum
        query = PostTraitSum.query.filter(PostTraitSum.topic_id == post.topic.id)
        sum_rel = query.filter(PostTraitSum.trait_id == post_trait.id).first()
        sum_rel.value += value

    db.session.commit()

def reconsiderPost (post):
  
    """
    recalculates the post trait values for a post already added to
    the trait registry and (if necessary) changes the cache sums    
    """

    query = Post.query.order_by(Post.created_at)
    post_id_oneples = query.limit(post_margin).values(Post.id)
    post_ids_in_margin = [oneple[0] for oneple in post_id_oneples]

    # if post is in the margin we first must
    # remove its old values from the sums
    if post.id in post_ids_in_margin: 
        for post_trait in PostTraitDispatcher():
            if not post_trait.is_relevant:
                continue
            # get trait value
            query = PostTraitValue.query.filter(PostTraitValue.post_id == post.id)
            query = query.filter(PostTraitValue.trait_id == post_trait.id)
            rel = query.first()
            value_for_subtraction = rel.value
            # subtract it
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == post.topic.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.id).first()
            sum_rel.value -= value_for_substraction

    # recalculate the trait values
    for post_trait in PostTraitDispatcher():
        if not post_trait.is_relevant:
            continue
        query = PostTraitValue.query.filter(PostTraitValue.post_id == post.id)
        query = query.filter(PostTraitValue.trait_id == post_trait.id)
        rel = query.first()
        new_value = post_trait.determine_value(post)
        rel.value = new_value
        
        if post.id in post_ids_in_margin: 
            # re-add to sum
            query = PostTraitSum.query.filter(PostTraitSum.topic_id == post.topic.id)
            sum_rel = query.filter(PostTraitSum.trait_id == post_trait.id).first()
            sum_rel.value += value
