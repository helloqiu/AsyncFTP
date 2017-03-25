# -*- coding: utf-8 -*-
import time
import os
import pwd
import grp
from stat import filemode


def get_mlsx(path):
    timefunc = time.gmtime
    for file in os.scandir(path):
        stat = file.stat()
        result = ""
        result += "modify={};".format(time.strftime("%Y%m%d%H%M%S", timefunc(stat[8])))
        result += "size={};".format(stat[6])
        result += "type={};".format("dir" if file.is_dir() else "file")
        result += " {}".format(file.name)
        yield result


def get_list(path):
    for file in os.scandir(path):
        stat = file.stat()
        perms = filemode(stat.st_mode)
        nlinks = stat.st_nlink
        if not nlinks:
            nlinks = 1
        size = stat.st_size
        try:
            uname = pwd.getpwuid(stat.st_uid).pw_name
        except:
            uname = 'owner'
        try:
            gname = grp.getgrgid(stat.st_gid).gr_name
        except:
            gname = 'group'
        mtime = time.gmtime(stat.st_mtime)
        mtime = time.strftime("%b %d %H:%M", mtime)
        mname = file.name
        yield "{}   {} {}    {}   {} {} {}".format(perms, nlinks, uname, gname, size, mtime, mname)
