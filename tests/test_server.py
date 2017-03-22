# -*- coding: utf-8 -*-

import pytest
from asyncftp.Server import BaseServer
from asyncftp.Authorizers import BaseAuthorizer


def test_init():
    with pytest.raises(ValueError) as e:
        BaseServer()
    assert e.value.args[0] == "The authorizier must not be None."
    authorizer = BaseAuthorizer()
    server = BaseServer(authorizer=authorizer)
    assert server.host == "127.0.0.1"
    assert server.port == 20
    assert server.authorizer == authorizer
