# -*- coding: utf-8 -*-
"""
Just another ftp server.

Usage: aysncftpd [-c CONFIG_FILE]

Options:
    -h --help     Show this screen.
    --version     Show version.
    -c=<CONFIG_FILE> Specify config file [default: ./config.json].
"""

import json
from docopt import docopt
from asyncftp import __version__
from asyncftp.Authorizers import BaseAuthorizer
from asyncftp.Server import BaseServer
from asyncftp.console.app import make_app
from asyncftp.Logger import enable_pretty_logging


def parse():
    arguments = docopt(__doc__, version=__version__)
    if not arguments["-c"]:
        arguments["-c"] = "./config.json"
    with open(arguments["-c"]) as f:
        config = json.loads(f.read())
    check_config(config)
    authorizer = BaseAuthorizer()
    for location in config["location"]:
        if location["auth"]["user"] == "anonymous":
            authorizer.add_anonymous(location["path"], perm=location["auth"]["perm"])
        else:
            authorizer.add_user(username=location["auth"]["user"],
                                password=location["auth"]["password"],
                                perm=location["auth"]["password"],
                                homedir=location["path"])
    server = BaseServer(
        host=config["host"],
        port=config["port"],
        authorizer=authorizer,
        ip_refuse=config["ip_refuse"]
    )
    enable_pretty_logging(server.logger, level='info')
    flask_app = make_app(server)
    enable_pretty_logging(flask_app.logger, level='info')
    flask_app.run(
        host=config["webui"]["host"],
        port=int(config["webui"]["port"]),
        debug=True
    )


def check_config(config):
    try:
        keys = config.keys()
        assert "host" in keys
        assert "port" in keys
        assert "location" in keys
        assert "webui" in keys
        assert "ip_refuse" in keys
        locations = config["location"]
        for location in locations:
            keys = location.keys()
            assert "path" in keys
            assert "auth" in keys
        webui = config["webui"]
        keys = webui.keys()
        assert "host" in keys
        assert "port" in keys
    except AssertionError:
        raise ValueError("Config file is invalid.")

parse()
