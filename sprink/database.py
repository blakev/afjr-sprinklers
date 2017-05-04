#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

import time
import logging
from datetime import datetime

from peewee import *

from sprink.constants import DATABASE_PATH

logger = logging.getLogger(__name__)
db = SqliteDatabase(DATABASE_PATH, threadlocals=True)


class BaseModel(Model):
    created = DateTimeField(default=datetime.utcnow)
    updated = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db

    def as_json(self):
        return self._data


class Sensor(BaseModel):
    name = CharField()
    alias = CharField(default=lambda: hex(int(time.time())))
    description = CharField(max_length=2048)
    gpio = IntegerField(unique=True)
    io_idx = IntegerField(unique=False, default=-1)

    class Meta:
        order_by = ('gpio', 'io_idx',)


class Reading(BaseModel):
    sensor = ForeignKeyField(Sensor, related_name='readings')
    num_value = FloatField(null=True)
    str_value = CharField(null=True)
    meta = CharField(max_length=4096)
    group = BigIntegerField()

    class Meta:
        order_by = ('-created',)


class History(BaseModel):
    name = CharField()
    description = CharField(null=True, max_length=4096)
    success = BooleanField(null=True)


tables = [Sensor, Reading, History]


def create_tables(force=True):
    """ Creates our tables in the database. """

    db.connect()
    if force:
        db.drop_tables(tables)
    try:
        db.create_tables(tables)
    except OperationalError as e:
        logger.error(e)
    finally:
        db.close()


def register_app(app):
    """ Opens and closes the database connection when routes are called in Flask. """

    @app.before_request
    def before_request():
        db.connect()

    @app.after_request
    def after_request(response):
        db.close()
        return response

    return app
