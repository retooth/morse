
from . import app
from flask import redirect, url_for
from ..models import db
from ..models.core import User, Group, GroupMember, GroupMode 
from ..models.filters import TopicFilter, PostFilter
from ..models.sorting import TopicSortingPreference
from ..api.dispatchers import TopicFilterDispatcher, PostFilterDispatcher

@app.route('/install')
def install ():
    """ 
    Creates base tables / installs default config
    :rtype: html
    """
    db.create_all()
    
    # !important: dont't change the order
    gadmin = Group("Administrators", True, True, True, True, True, 4)
    gmods = Group("Moderators", False, True, True, True, True, 3)
    gregistered = Group("Registered", False, False, False, False, False, 2)
    gguests = Group("Guests", False, False, False, False, False, 1)
    
    db.session.add(gadmin)
    db.session.add(gmods)
    db.session.add(gregistered)
    db.session.add(gguests)

    admin = User("admin", "admin", "root@localhost")
    db.session.add(admin)
    db.session.commit()

    rel = GroupMember(admin.id,gadmin.id)
    mode1 = GroupMode(0, gadmin.id, True, True) 
    mode2 = GroupMode(0, gmods.id, True, True) 
    mode3 = GroupMode(0, gregistered.id, True, True) 
    mode4 = GroupMode(0, gguests.id, True, False) 

    db.session.add(rel)
    db.session.add(mode1)
    db.session.add(mode2)
    db.session.add(mode3)
    db.session.add(mode4)

    spreference = TopicSortingPreference(admin.id)
    db.session.add(spreference)

    topic_filter_dispatcher = TopicFilterDispatcher()
    for filter_blueprint in topic_filter_dispatcher:
        filter_entry = TopicFilter(admin.id, filter_blueprint.id)
        db.session.add(filter_entry)

    post_filter_dispatcher = PostFilterDispatcher()
    for filter_blueprint in post_filter_dispatcher:
        filter_entry = PostFilter(admin.id, filter_blueprint.id)
        db.session.add(filter_entry)

    db.session.commit()

    return redirect(url_for('index'))
