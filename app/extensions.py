# -*- coding: utf-8 -*-
"""
Flask extensions instances, for access outside app.factory
"""

from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

from lib.oidc import OIDC


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


db = SQLAlchemy()

oidc = OIDC()

user_datastore = SQLAlchemyUserDatastore(db, None, None)
