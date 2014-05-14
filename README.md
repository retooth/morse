# Morse

A javascript-heavy, minimalist bulletin board software

#### Motivation

Morse was created, because phpBB and vBulletin seemed outdated to me, both in design and ux.
The main reason the ux bugged me was, that the mass of shown information (such as post dates,
"active since" and the like) distracted from the actual content. I tried a new approach I'd
like to call the "SIOWN principle", which is short for "Show Information Only When Needed"
In application this means, that the new post input field only shows, when the user starts
typing, additional post info shows only when you hover over the username, etc

Another thing that was bugging me in particular was the post-read bevaviour. If I click a thread
in phpBB or vBulletin the threads gets automatically flagged as "read". But what if I click
a thread by accident or open it, but don't read to the end (e.g. I close the tab, because I 
suddenly notice, that my pasta water is boiling over). I have to remember flagging it as
unread. In Morse a post gets only flagged, when the bottom of the post is in the browser
viewport, which means you actually have to read the post (or scroll down like a maniac)

#### Current version

Morse is not really finished yet. It lacks an admin panel and some small features. But if 
you want to hack into the code and temper with the database yourself, you can try it already. 
