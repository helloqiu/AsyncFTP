# -*- coding: utf-8 -*-
import json
from flask import Flask
from flask import request
from flask import jsonify
import time
from psutil import net_io_counters
from asyncftp import __version__
import threading
from asyncftp.Logger import _LogFormatter

t = time.time()
net = net_io_counters()
formatter = _LogFormatter(color=False)
log_message = str()


def make_app(server, queue):
    app = Flask(__name__)

    @app.route('/api/info', methods=['GET'])
    def speed():
        if request.method == 'GET':
            global t
            global net
            temp_t = time.time()
            p = net_io_counters()
            result = dict()
            result['speed'] = dict(
                up=(p[0] - net[0]) / (temp_t - t),
                down=(p[1] - net[1]) / (temp_t - t)
            )
            result['up_time'] = server.up_time
            result['running'] = True if server.up_time else False
            t = temp_t
            net = p
            return jsonify(result)

    @app.route('/api/start', methods=['GET'])
    def run_server():
        if not server.running:
            thread = threading.Thread(target=server.run)
            thread.start()
        return 'ok'

    @app.route('/api/stop', methods=['GET'])
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
                'refuse_ip': server.ip_refuse
            })
        if request.method == 'POST':
            data = json.loads(request.data.decode('utf-8'))
            for ip in data['refuse_ip']:
                server.add_refuse_ip(ip)
            return 'ok'

    @app.route('/api/log', methods=['GET'])
    def log():
        if request.method == 'GET':
            result = str()
            while not queue.empty():
                record = queue.get(block=False)
                result += formatter.format(record) + '\n'
            global log_message
            log_message += result
            return log_message

    return app
