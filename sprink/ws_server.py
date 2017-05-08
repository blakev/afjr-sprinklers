#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# >>
#   © Vivint, inc. 2017
#   blake, afjr-sprinklers
# <<

from gevent.monkey import patch_all
patch_all()

from flask import Flask, render_template, jsonify
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

HOST, PORT = 'localhost', 8000
DEBUG = True


class SensorStream(WebSocketApplication):
    def on_open(self):
        print('connection opened')

    def on_message(self, message, *args, **kwargs):
        print(message, args, kwargs)
        self.ws.send(message)

    def on_close(self, *args, **kwargs):
        reason = args[0]
        print(reason)


if __name__ == '__main__':
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/info')
    def info():
        return jsonify({
            'server': {
                'host': HOST,
                'port': PORT,
                'debug': DEBUG
            },
            'ws_conn': 'ws://%s:%d/ws' % (HOST, PORT)
        })

    resources = Resource([
        ('/',   app),
        ('/ws', SensorStream)
    ])

    server = WebSocketServer((HOST, PORT), resources, debug=DEBUG)
    server.serve_forever()
