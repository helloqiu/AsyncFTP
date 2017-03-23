# -*- coding: utf-8 -*-

proto_cmds = {
    'USER': dict(
        perm=None, auth=False, arg=True
    ),
    'PASS': dict(
        perm=None, auth=False, arg=True
    ),
    'PASV': dict(
        perm=None, auth=True, arg=False
    ),
    'MLSD': dict(
        perm='l', auth=True, arg=None
    ),
    'PWD': dict(
        perm=None, auth=True, arg=None
    ),
    'TYPE': dict(
        perm=None, auth=True, arg=True
    )
}
