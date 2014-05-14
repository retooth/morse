#!/usr/bin/python
# Pool configuration file

DATABASE = 'morse.db'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE
SQLALCHEY_ECHO = True

DEBUG = True

SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
