# -*- coding: utf-8 -*-

from asyncftp.utils import parse_message, get_cmd


def test_parse_message():
    assert parse_message(200, "喵喵喵") == "{} {}\r\n".format(200, "喵喵喵").encode('utf-8')


def test_get_cmd():
    CMD = "LIST\r\n".encode('utf-8')
    cmd, arg = get_cmd(CMD)
    assert cmd == 'LIST'
    assert arg is None
    CMD = "LIST 喵喵喵\r\n".encode('utf-8')
    cmd, arg = get_cmd(CMD)
    assert cmd == 'LIST'
    assert arg == '喵喵喵'
