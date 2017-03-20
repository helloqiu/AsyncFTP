# -*- coding: utf-8 -*-

import os
import pytest
from asyncftp.Authorizers import BaseAuthorizer


def test_user_table():
    authorizer = BaseAuthorizer()
    assert authorizer.user_table == dict()


def test_has_user():
    authorizer = BaseAuthorizer()
    assert not authorizer.has_user("喵喵喵")
    homedir = os.path.join(os.getcwd(), "tests")
    authorizer.add_user(
        username="喵喵喵",
        password="喵喵",
        homedir=homedir
    )
    assert authorizer.has_user("喵喵喵")
    user = authorizer.user_table["喵喵喵"]
    assert user["pwd"] == "喵喵"
    assert user["perm"] == "elr"
    assert user["home"] == homedir

    with pytest.raises(ValueError) as e:
        authorizer.add_user("喵喵喵", "喵喵", homedir)
    assert e.value.args[0] == 'user {} already exists'.format("喵喵喵")

    with pytest.raises(ValueError) as e:
        authorizer.add_user("喵喵", "喵喵", "喵喵喵~")
    assert e.value.args[0] == '{} is not a valid directory'.format("喵喵喵~")


def test_check_permissions():
    authorizer = BaseAuthorizer()
    with pytest.raises(ValueError) as e:
        authorizer.check_permissions("喵")
    assert e.value.args[0] == '{} is not a valid permission'.format("喵")
    authorizer.check_permissions("elradfmwM")
