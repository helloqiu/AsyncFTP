# -*- coding: utf-8 -*-

import os
from asyncftp.Authorizers import BaseAuthorizer
from asyncftp.Server import BaseServer

if __name__ == "__main__":
    authorizer = BaseAuthorizer()
    authorizer.add_anonymous(os.path.join(os.getcwd(), "tests"), perm='elrwdf')
    server = BaseServer(authorizer=authorizer, port=8888)
    server.run()
