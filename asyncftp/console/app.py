# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import jsonify
import time
from psutil import net_io_counters
from asyncftp import __version__
import threading


def make_app(server):
    app = Flask(__name__)

    @app.route('/api/speed', methods=['GET'])
    def speed():
        if request.method == 'GET':
            p = net_io_counters()
            result = dict(
                up=p[0],
                down=p[1]
            )
            return jsonify(result)

    @app.route('/api/run', methods=['GET'])
    def run_server():
        if not server.running:
            thread = threading.Thread(target=server.run)
            thread.start()
        return 'ok'

    @app.route('/api/close', methods=['GET'])
    def close_server():
        server.close()
        return 'ok'

    @app.route('/api/config', methods=['GET', 'POST'])
    def config():
        if request.method == 'GET':
            return jsonify({
                'host': server.host,
                'port': str(server.port),
                'version': __version__,
                'uptime': server.up_time,
                'refuse_ip': server.ip_refuse
            })

    return app
