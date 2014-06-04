#!/usr/bin/python

from morse import *
from morse.models import Group, GroupMember, GroupMode, User

print "creating tables...",
with app.app_context():
    db.create_all()
    print "done"
    print "configuring defaults...",
    
    # !important: dont't change the order
    gadmin = Group("Administrators", "All Access Granted", True, True, True, True, 4)
    gmods = Group("Moderators", "Can close/edit threads", False, True, True, True, 3)
    gregistered = Group("Registered", "All Registered Users", False, False, False, False, 2)
    gguests = Group("Guests", "Users without a login", False, False, False, False, 1)
    
    db.session.add(gadmin)
    db.session.add(gmods)
    db.session.add(gregistered)
    db.session.add(gguests)

    admin = User("admin", "admin", "root@localhost")
    db.session.add(admin)
    db.session.commit()

    rel = GroupMember(admin.id,gadmin.id)
    mode1 = GroupMode(0, gadmin.id, True, True, True) 
    mode2 = GroupMode(0, gmods.id, True, True, True) 
    mode3 = GroupMode(0, gregistered.id, True, True, True) 
    mode4 = GroupMode(0, gguests.id, True, False, True) 

    db.session.add(rel)
    db.session.add(mode1)
    db.session.add(mode2)
    db.session.add(mode3)
    db.session.add(mode4)

    db.session.commit()
    print "done"
    print "Yay! All done. Run runserver.py and log in with admin/admin"
