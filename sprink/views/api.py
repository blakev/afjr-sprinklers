#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

import logging
from functools import wraps

from flask import Blueprint, jsonify

from sprink.database import db, Sensor, IntegrityError

logger = logging.getLogger(__name__)
blu = Blueprint('api', __name__, url_prefix='/api')


def json_response(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        ret = fn(*args, **kwargs)
        if isinstance(ret, dict):
            v = ret
        elif isinstance(ret, tuple):
            err, resp = ret
            v = {
                'error': err,
                'response': resp}
        else:
            logger.info('bad response from %s', fn.__name__)
            v = {
                'error': None,
                'response': str(ret)}
        return jsonify(v)
    return inner


@blu.route('/sensors', methods=['GET', 'POST'])
@json_response
def sensors():
    error, response = None, None
    try:
        with db.transaction():
            sensor = Sensor.create(name='dht11',
                                   description='Temperature and Humidity',
                                   gpio=25,
                                   io_idx=-1)
            logger.info(sensor)

    except IntegrityError as e:
        error = str(e)
        logger.exception(e)
    else:
        response = {'sensors': [s.as_json() for s in Sensor.select()]}
    return error, response


@blu.route('/history', methods=['GET', 'POST'])
@json_response
def _history():
    return 'Not Implemented', None


@blu.route('/readings', methods=['GET', 'POST'])
@json_response
def readings():
    return 'Not Implemented', None
