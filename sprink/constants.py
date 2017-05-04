#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

import os

ROOT_DIR = os.path.dirname(os.path.split(os.path.abspath(__file__))[0])
CODE_DIR = os.path.join(ROOT_DIR, 'sprink')
RESOURCES = os.path.join(ROOT_DIR, 'resources')

DATABASE_PATH = os.path.join(RESOURCES, 'db.sqlite')
FLASK_CONFIG = os.path.join(RESOURCES, 'flask.json')

if __name__ == '__main__':
    # run our tests, but only if this file is run by itself
    assert os.path.dirname(__file__) == CODE_DIR

    # check for our logging configuration
    assert os.path.isfile(os.path.join(RESOURCES, 'logging.cfg'))
