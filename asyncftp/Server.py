# -*- coding: utf-8 -*-

from curio import run, spawn
from curio.socket import *


class BaseServer(object):
    """
    The base FTP server.
    """

    def __init__(self, host="127.0.0.1", port=20, authorizer=None):
        if authorizer is None:
            raise ValueError("The authorizier must not be None.")
        self.host = host
        self.port = port
        self.authorizer = authorizer
