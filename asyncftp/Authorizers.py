# -*- coding: utf-8 -*-

"""
An "authorizer" is designed for handling authentications and permissions
of the FTP server. It has functions:
- verifying user's name and password
- getting user home directory
- checking user permissions
"""
import os


class BaseAuthorizer(object):
    """
    Just a base authorizer. But it has the capability to do all things
    an authorizer should do.
    """
    read_perms = "elr"
    write_perms = "adfmwM"

    def __init__(self):
        self.user_table = dict()

    def has_user(self, username):
        """
        Check if the authorizer has a user.
        :param username: The username you want to check.
        :return: True if the authorizer has the user. Otherwise False.
        """
        return username in self.user_table

    def check_permissions(self, perm):
        """
        Check if the permissions are valid.
        If one is not valid, raise a ValueError.
        :param perm: The permissions you want to check.
        :return: None
        """
        for p in perm:
            if p not in self.read_perms + self.write_perms:
                raise ValueError('{} is not a valid permission'.format(p))

    def add_user(self, username, password, homedir, perm='elr'):
        """
        Add a user to the virtual user table.

        User's Permissions:

        Read Permissions:
        - "e" = change directory (CWD)
        - "l" = list files (List, NLST, STAT, MLSD, MLST, SIZE, MDTM)
        - "r" = retrieve file from server (RETR)

        Write Permissions:
        - "a" = append data to an existing file (APPE)
        - "d" = delete file or dir (DELE, RMD)
        - "f" = rename file or dir (RNFR, RNTO)
        - "m" = create dir (MKD)
        - "w" = store a file to server (STOR, STOU)
        - "M" = change file mode (SITE CHMOD)

        :param username: The username of the virtual user.
        :param password: The password of the virtual user.
        :param homedir: The home directory of the virtual user.
        :param perm: The permissions granted to the virtual user.
        :return: None
        """
        if self.has_user(username):
            raise ValueError('user {} already exists'.format(username))
        if not os.path.isdir(homedir):
            raise ValueError('{} is not a valid directory'.format(homedir))
        homedir = os.path.realpath(homedir)
        self.check_permissions(perm)
        self.user_table[username] = dict(
            pwd=password,
            home=homedir,
            perm=perm,
        )
        return None

    def add_anonymous(self, homedir, **kwargs):
        """
        Add an anonymous user to the virtual user table.
        :param homedir: The home directory of the virtual user.
        :param kwargs:
        :return: None
        """
        self.add_user(
            username="anonymous",
            password="",
            homedir=homedir,
            **kwargs
        )
