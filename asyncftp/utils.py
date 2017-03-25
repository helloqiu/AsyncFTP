# -*- coding: utf-8 -*-


def parse_message(code, message):
    return "{} {}\r\n".format(code, message).encode("utf-8")
