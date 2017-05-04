#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

import logging

from flask import Blueprint

logger = logging.getLogger(__name__)
blu = Blueprint('base', __name__, url_prefix='')


@blu.route('/')
def index():
    return 'hello'
