#/usr/bin/python

from sqlalchemy.exc import SQLAlchemyError

class NotPersistentError (SQLAlchemyError):
    pass
