# -*- coding: utf-8 -*-

import os
import time
from asyncftp.fs2ftp import get_mlsx


def test_get_mlsx():
    path = os.path.join(os.getcwd(), "tests")
    result = {}
    temp = get_mlsx(path)
    for f in temp:
        f = f.split(";")
        filename = f[3].strip()
        result[filename] = {}
        for i in range(0, 3):
            name = f[i].split('=')[0]
            result[filename][name] = f[i].split('=')[1]
    files = os.scandir(path)
    for file in files:
        assert file.name in result.keys()
        result_file = result[file.name]
        stat = file.stat()
        assert result_file['modify'] == str(time.strftime("%Y%m%d%H%M%S", time.gmtime(stat[8])))
        assert result_file['size'] == str(stat[6])
        assert result_file['type'] == "dir" if file.is_dir() else "file"
