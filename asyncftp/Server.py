# -*- coding: utf-8 -*-

import time
import os
from asyncftp.Logger import enable_pretty_logging, logger
from asyncftp import __version__
from asyncftp.cmd import proto_cmds
from curio import run, spawn, run_in_thread, Queue
from curio.socket import *


class BaseServer(object):
    """
    The base FTP server.
    """

    banner = "AsyncFTP {} ready.".format(__version__)

    def __init__(self, host="127.0.0.1", port=20, authorizer=None,
                 ip_refuse=set()):
        if authorizer is None:
            raise ValueError("The authorizier must not be None.")
        self.host = host
        self.port = port
        self.authorizer = authorizer
        self.ip_refuse = ip_refuse
        self.ip_table = dict()
        self.logger = logger
        enable_pretty_logging(self.logger, level="debug")

    def run(self):
        run(self._run)

    async def _run(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        self.logger.info("FTP Server is listening at {}:{}".format(self.host, self.port))
        async with sock:
            while True:
                client, addr = await sock.accept()
                if addr[0] not in self.ip_refuse:
                    await spawn(self.handle_connection, client, addr)
                else:
                    self.logger.info("Refuse connection from {}".format(addr))

    async def handle_connection(self, client, addr):
        self.logger.info("Connection from {}".format(addr))
        async with client:
            if addr[0] not in self.ip_table.keys():
                self.logger.debug("Connection {} is a new connection".format(addr))
                self.ip_table[addr[0]] = dict(
                    port=addr[1],
                    auth=False,
                    username=None,
                    DTPServer=None,
                    path=None
                )
                await client.sendall(self.parse_message(220, self.banner))
            while True:
                self.logger.debug("Waiting for message from {}".format(addr))
                d = await client.recv(1000)
                self.logger.debug("Receive message from {}.\nContent:\n{}".format(addr, d))
                if not d:
                    self.logger.debug("No content in message from {}.".format(addr))
                    break
                else:
                    cmd, arg = self.get_cmd(d)
                    self.logger.info("GET command \"{}\" arg \"{}\"".format(cmd, arg))
                    username = self.ip_table[addr[0]]['username']
                    if cmd not in proto_cmds.keys():
                        await client.sendall(self.parse_message(500, 'Command "{}" not understood.'.format(cmd)))
                        continue
                    elif proto_cmds[cmd]['auth'] and not self.ip_table[addr[0]]['auth']:
                        await client.sendall(self.parse_message(332, 'Need account for login.'))
                        continue
                    # Check permission
                    if proto_cmds[cmd]['perm']:
                        self.logger.debug("Checking permission.")
                        self.logger.debug("Require permission: \"{}\"".format(proto_cmds[cmd]['perm']))
                        home = self.authorizer.user_table[username]['home']
                        self.logger.debug("Home dir: \"{}\"".format(home))
                        self.logger.debug("Virtual dir: \"{}\"".format(self.ip_table[addr[0]]['path']))
                        self.logger.debug(
                            "Join path: \"{}\"".format(os.path.join(home, self.ip_table[addr[0]]['path'])))
                        if not self.authorizer.has_perm(
                                username,
                                proto_cmds[cmd]['perm'],
                                os.path.join(
                                    home,
                                    self.ip_table[addr[0]]['path']),
                        ):
                            await client.sendall(self.parse_message(550, 'Not enough privileges.'))
                            continue
                    if cmd == 'USER':
                        self.ip_table[addr[0]]['username'] = arg
                        await client.sendall(self.parse_message(331, 'Username ok, send password.'))
                    elif cmd == 'PASS':
                        self.logger.debug("Checking password of \"{}\"".format(username))
                        if not username:
                            self.ip_table[addr[0]]['auth'] = False
                            await client.sendall(self.parse_message(503, "Bad sequence of commands."))
                        if (self.authorizer.has_user(username) and self.authorizer.user_table[username]["pwd"] == arg) \
                                or username == "anonymous":
                            self.ip_table[addr[0]]['auth'] = True
                            self.ip_table[addr[0]]['path'] = ''
                            await client.sendall(self.parse_message(230, "Login successful."))
                        else:
                            self.ip_table[addr[0]]['auth'] = False
                            await client.sendall(self.parse_message(530, "Not logged in :("))
                    elif cmd == 'PASV':
                        server = BaseDTPServer(self.host, addr[0])
                        self.ip_table[addr[0]]['DTPServer'] = server
                        await spawn(server.run)
                        await client.sendall(
                            self.parse_message(227, "Entering passive mode {}.".format(server.getsockname())))
                    elif cmd == 'MLSD':
                        result = self.get_mlsx(
                            os.path.realpath(
                                os.path.join(
                                    self.authorizer.user_table[username]["home"],
                                    self.ip_table[addr[0]]['path'])))
                        async for f in result:
                            await self.ip_table[addr[0]]['DTPServer'].send(f + "\r\n")

        self.ip_table.pop(addr[0])
        self.logger.info("Connection {} closed".format(addr))

    @staticmethod
    def parse_message(code, message):
        return "{} {}\r\n".format(code, message).encode("utf-8")

    @staticmethod
    def get_cmd(data):
        data = data.decode('utf-8').strip()
        cmd = data.split(' ')[0].upper()
        arg = data[len(cmd) + 1:]
        return cmd, arg

    @staticmethod
    async def get_mlsx(path):
        timefunc = time.gmtime
        for file in os.scandir(path):
            stat = file.stat()
            result = ""
            result += "modify={};".format(time.strftime("%Y%m%d%H%M%S", timefunc(stat[8])))
            result += "size={};".format(stat[6])
            result += "type={};".format("dir" if file.is_dir() else "file")
            result += " {}".format(file.name)
            yield result


class BaseDTPServer(object):
    def __init__(self, host, ip):
        self.ip = ip
        self.queue = Queue()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((host, 0))
        self.sock.listen(5)
        self.connected = False

    def getsockname(self):
        sockname = self.sock.getsockname()
        result = tuple()
        ip = sockname[0]
        port = sockname[1]
        for p in ip.split('.'):
            result += (int(p),)
        result += (port >> 8,)
        result += (port - (port >> 8 << 8),)
        return result

    async def run(self):
        logger.info("DTP Server listening on {}".format(self.sock.getsockname()))
        async with self.sock:
            client, addr = await self.sock.accept()
            if addr[0] == self.ip:
                if self.connected:
                    logger.error("DTP Server is already connected.")
                else:
                    self.connected = True
                    logger.info("DTP Server get connection from {}".format(addr))
                    s = client.as_stream()
                    while True:
                        message = await self.queue.get()
                        logger.debug("DTP Server get send message.")
                        await s.write(message)
            else:
                logger.info("DTP Server refuses connection from {}".format(addr))

    async def send(self, message):
        logger.debug("DTP Server put message into queue.")
        await self.queue.put(message.encode('utf-8'))
