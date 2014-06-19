#!/usr/bin/python
# Pool configuration file

DATABASE = 'morse'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2:///' + DATABASE
SQLALCHEY_ECHO = True

DEBUG = True

SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
