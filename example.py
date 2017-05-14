# -*- coding: utf-8 -*-

import os
from asyncftp.Authorizers import BaseAuthorizer
from asyncftp.Server import BaseServer
from asyncftp.Logger import enable_pretty_logging

if __name__ == "__main__":
    authorizer = BaseAuthorizer()
    authorizer.add_anonymous(os.path.join(os.getcwd(), "tests"), perm='elrwdf')
    server = BaseServer(authorizer=authorizer, port=2122)
    enable_pretty_logging(server.logger)
    server.run()
