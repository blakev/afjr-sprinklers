#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

import os
import logging
from logging.config import fileConfig

from flask import Flask

import sprink.constants as c
from sprink.database import create_tables, register_app as db_register_app
from sprink.views import api, base

fileConfig(os.path.join(c.RESOURCES, 'logging.cfg'))
logger = logging.getLogger(__name__)


def create_app(**kwargs):
    app = Flask(__name__)
    app.config.from_json(c.FLASK_CONFIG)

    # create the database tables
    create_tables(force=kwargs.get('FORCE_DB_TABLES', False))
    # open/close database connections when views are requested
    db_register_app(app)

    # register our view endpoints
    for v in [api, base]:
        blu = getattr(v, 'blu', None)
        if blu is None:
            raise ValueError('no blueprint defined as `blu` in module %s' % v.__name__)
        logger.info('registering blueprint, %s', blu.name)
        app.register_blueprint(blu)

    return app


app = create_app()

if __name__ == '__main__':
    app.run('localhost', 8900, debug=True)
