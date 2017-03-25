# -*- coding: utf-8 -*-


def parse_message(code, message):
    return "{} {}\r\n".format(code, message).encode("utf-8")


def get_cmd(data):
    data = data.decode('utf-8').strip()
    cmd = data.split(' ')[0].upper()
    arg = data[len(cmd) + 1:]
    arg = None if not arg else arg
    return cmd, arg
