# -*- coding: utf-8 -*-

from asyncftp.utils import parse_message


def test_parse_message():
    assert parse_message(200, "喵喵喵") == "{} {}\r\n".format(200, "喵喵喵").encode('utf-8')
