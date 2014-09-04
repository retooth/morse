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

from multiprocessing import Process, Value
from ctypes import c_bool, c_uint32
from models.discussion import Topic, Post
from models.traits import PostTrait
from models import db
from datetime import datetime

class TaskDispatcher (object):

    __monostate = None

    def __init__ (self):
        if not TaskDispatcher.__monostate:
            TaskDispatcher.__monostate = self.__dict__
            self._tasks = {}
        else:
            self.__dict__ = TaskDispatcher.__monostate

    def fetch_task (self, identifier):
        return self._tasks[identifier]

    def start_task (self, identifier, task):
        if identifier in self._tasks:
            raise KeyError("Identifier " + identifier + " is already used")
        task.start()
        self._tasks[identifier] = task

class Task (object):

    def __init__ (self, f, *additional_args):
        self.shared_done = Value(c_bool, False)
        self.shared_items_done = Value(c_uint32, 0)
        self.shared_items_count = Value(c_uint32, 0)
        args = (self.shared_done, self.shared_items_done, self.shared_items_count) + additional_args
        self.process = Process(target = f, args = args)
        self.time_started = None

    def start (self):
        self.process.start() 
        self.time_started = datetime.now()

    @property
    def is_done (self):
        return self.shared_done.value

    @property
    def progress_in_percent (self):
        items_done = self.shared_items_done.value         
        items_count = self.shared_items_count.value         
        return items_done * 100.0 / items_count

    @property
    def estimated_time_left (self):
        if self.time_started is None:
            raise AssertionError("Task was not yet started")
        time_passed = datetime.now() - self.time_started
        average_time_needed_to_process_one_item = time_passed / self.shared_items_done.value
        items_left = self.shared_items_count.value - self.shared_items_count.value
        return items_left * avagere_time_needed_to_process_one_item

def recalculate_all_interesting_values (shared_done, shared_topics_done, shared_topic_count):
    
    #FIXME this section could cause severe memory 
    #problems when there is a huge number of topics
    all_topics = Topic.query.all()
    shared_topic_count.value = len(all_topics)

    for topic in all_topics:
        topic.calculate_interesting()
        shared_topics_done.value += 1

    db.commit()
    shared_done.value = True

def install_post_traits (shared_done, shared_posts_done, shared_posts_count, post_traits):

    for post_trait in post_traits:
        registered_post_trait = PostTrait(post_trait.string_identifier)
        db.session.add(registered_post_trait)

    #FIXME this section could cause severe memory 
    #problems when there is a huge number of posts
    all_posts = Post.query.all()
    shared_posts_count.value = len(all_posts)

    for post in all_posts:
        for post_trait in post_traits:
            value = post_trait.determine_value(post)
            value_entry = PostTraitValue(post.id, post_trait.string_identifier, value)
            db.session.add(value_entry)
        shared_posts_done.value += 1

    db.session.commit()
    shared_done.value = True
