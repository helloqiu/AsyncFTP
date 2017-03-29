# -*- coding: utf-8 -*-

import os

try:
    from os import sendfile
except ImportError:
    from sendfile import sendfile
from asyncftp.Logger import enable_pretty_logging, logger
from asyncftp import __version__
from asyncftp.cmd import proto_cmds
from asyncftp.fs2ftp import get_mlsx, get_list
from asyncftp.utils import parse_message, get_cmd
from curio import run, spawn, Queue, sleep
from curio.socket import *

BINARY = 0
ASCII = 1


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
            if addr not in self.ip_table.keys():
                self.logger.debug("Connection {} is a new connection".format(addr))
                self.ip_table[addr] = dict(
                    port=addr[1],
                    auth=False,
                    username=None,
                    DTPServer=None,
                    path=None,
                    type=BINARY,
                    rnfr=None
                )
                await client.sendall(parse_message(220, self.banner))
            while True:
                self.logger.debug("Waiting for message from {}".format(addr))
                d = await client.recv(1000)
                self.logger.debug("Receive message from {}.\nContent:\n{}".format(addr, d))
                if not d:
                    self.logger.debug("No content in message from {}.".format(addr))
                    break
                else:
                    cmd, arg = get_cmd(d)
                    user = self.get_ip(addr)
                    self.logger.info("GET command \"{}\" arg \"{}\"".format(cmd, arg))
                    username = user['username']
                    if cmd not in proto_cmds.keys():
                        await client.sendall(parse_message(500, 'Command "{}" not understood.'.format(cmd)))
                        continue
                    elif proto_cmds[cmd]['auth'] and not user['auth']:
                        await client.sendall(parse_message(332, 'Need account for login.'))
                        continue
                    # Check permission
                    if proto_cmds[cmd]['perm']:
                        self.logger.debug("Checking permission.")
                        self.logger.debug("Require permission: \"{}\"".format(proto_cmds[cmd]['perm']))
                        home = self.get_user(username)['home']
                        self.logger.debug("Home dir: \"{}\"".format(home))
                        self.logger.debug("Virtual dir: \"{}\"".format(user['path']))
                        self.logger.debug(
                            "Join path: \"{}\"".format(os.path.join(home, user['path'])))
                        if not self.authorizer.has_perm(
                                username,
                                proto_cmds[cmd]['perm'],
                                os.path.join(
                                    home,
                                    user['path']),
                        ):
                            await client.sendall(parse_message(550, 'Not enough privileges.'))
                            if server.connected:
                                await server.close()
                            continue
                    if cmd == 'USER':
                        user['username'] = arg
                        await client.sendall(parse_message(331, 'Username ok, send password.'))
                    elif cmd == 'PASS':
                        self.logger.debug("Checking password of \"{}\"".format(username))
                        if not username:
                            user['auth'] = False
                            await client.sendall(parse_message(503, "Bad sequence of commands."))
                        if (self.authorizer.has_user(username) and self.get_user(username)["pwd"] == arg) \
                                or username == "anonymous":
                            user['auth'] = True
                            user['path'] = ''
                            await client.sendall(parse_message(230, "Login successful."))
                        else:
                            user['auth'] = False
                            await client.sendall(parse_message(530, "Not logged in :("))
                    elif cmd == 'PASV':
                        server = BaseDTPServer(self.host, addr[0])
                        user['DTPServer'] = server
                        await spawn(server.run, client)
                        await server.ready_and_send(client)
                    elif cmd == 'MLSD':
                        result = get_mlsx(
                            os.path.realpath(
                                os.path.join(
                                    self.get_user(username)["home"],
                                    user['path'])))
                        for f in result:
                            await user['DTPServer'].send(f + "\r\n")
                    elif cmd == 'PWD':
                        await client.sendall(
                            parse_message(257, "\"/{}\" is the current directory.".format(
                                user['path'])))
                    elif cmd == 'TYPE':
                        arg = arg.upper()
                        if arg == 'I':
                            user['type'] = BINARY
                            await client.sendall(parse_message(200, "Type set to Binary."))
                        elif arg == 'A':
                            user['type'] = ASCII
                            await client.sendall(parse_message(200, "Type set to Ascii."))
                        else:
                            await client.sendall(parse_message(500, "Type \"{}\" is unknown".format(arg)))
                    elif cmd == 'FEAT':
                        await client.sendall(parse_message('',
                                                           '211-Features supported:\n MLST type*;size*;modify*;\n211 End FEAT.'))
                    elif cmd == 'LIST':
                        server = user['DTPServer']
                        result = get_list(
                            os.path.join(
                                self.get_user(username)['home'],
                                user['path']
                            )
                        )
                        if not server.connected:
                            await client.sendall(
                                parse_message(150, 'File status okay. About to open data connection.'))
                        else:
                            await client.sendall(
                                parse_message(125, 'Data connection already open. Transfer starting.')
                            )
                        for f in result:
                            await server.send(f + "\r\n")
                        await server.send("\r\n")
                    elif cmd == 'CWD':
                        if arg[0] == '/':
                            path = arg[1:]
                        else:
                            path = os.path.join(user['path'], arg)
                        if len(path) > 0 and path[len(path) - 1] != '/':
                            path += '/'
                        if '..' in path:
                            path = path.replace('..', '/..')
                        real_path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                path
                            )
                        )
                        self.logger.debug("CWD get path \"{}\"".format(real_path))
                        if os.path.exists(real_path) and arg:
                            user['path'] = os.path.normpath(path)
                            self.logger.debug("CWD change path to\"{}\"".format(user['path']))
                            await client.sendall(parse_message(250, 'Directory successfully changed.'))
                        else:
                            await client.sendall(parse_message(550, 'Failed to change directory.'))
                    elif cmd == 'RETR':
                        server = user['DTPServer']
                        if not arg:
                            await client.sendall(parse_message(554, 'Invalid RETR parameter'))
                            await server.close()
                            continue
                        path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                os.path.join(
                                    user['path'], arg
                                )
                            )
                        )
                        if not os.path.isfile(path):
                            await client.sendall(parse_message(554, 'Invalid RETR parameter'))
                            await server.close()
                            continue
                        self.logger.debug('RETR get path "{}".'.format(path))
                        await server.sendfile(path)
                    elif cmd == 'STOR':
                        server = user['DTPServer']
                        if not arg:
                            await client.sendall(parse_message(554, 'Invalid STOR parameter'))
                            await server.close()
                            continue
                        path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                os.path.join(
                                    user['path'], arg
                                )
                            )
                        )
                        if os.path.isfile(path):
                            await client.sendall(parse_message(554, 'Invalid STOR parameter'))
                            await server.close()
                            continue
                        await client.sendall(parse_message(150, 'File status okay. About to open data connection.'))
                        # Wait DTP Server to get ready
                        while True:
                            if server.sock_client:
                                break
                            self.logger.debug('Waiting DTP server to get ready.')
                            await sleep(0.05)
                        with open(path, mode='w+b') as f:
                            async for data in server.recv():
                                f.write(data)
                        await client.sendall(parse_message(226, 'Transfer complete.'))
                    elif cmd == 'DELE':
                        if not arg:
                            await client.sendall(parse_message(501, 'Command needs an argument.'))
                            continue
                        path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                os.path.join(
                                    user['path'], arg
                                )
                            )
                        )
                        if not os.path.isfile(path):
                            await client.sendall(parse_message(550, 'No such file or directory.'))
                            continue
                        os.remove(path)
                        self.logger.debug('Delete file {}.'.format(path))
                        await client.sendall(parse_message(250, 'File removed.'))
                    elif cmd == 'RNFR':
                        if not arg:
                            await client.sendall(parse_message(501, 'Command needs an argument.'))
                            continue
                        path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                os.path.join(
                                    user['path'], arg
                                )
                            )
                        )
                        if not os.path.isfile(path):
                            await client.sendall(parse_message(550, 'No such file or directory.'))
                            continue
                        user['rnfr'] = path
                        await client.sendall(parse_message(350, 'Ready for destination name.'))
                    elif cmd == 'RNTO':
                        if not arg:
                            await client.sendall(parse_message(501, 'Command needs an argument.'))
                            continue
                        if not user['rnfr']:
                            await client.sendall(parse_message(503, 'Bad sequence of commands: use RNFR first.'))
                            continue
                        path = os.path.realpath(
                            os.path.join(
                                self.get_user(username)['home'],
                                os.path.join(
                                    user['path'], arg
                                )
                            )
                        )
                        os.rename(user['rnfr'], path)
                        user['rnfr'] = None
                        await client.sendall(parse_message(250, 'Renaming ok.'))
                    elif cmd == 'QUIT':
                        await client.sendall(parse_message(220, 'Goodbye! :)'))
                        break

        self.ip_table.pop(addr)
        self.logger.info("Connection {} closed".format(addr))

    def get_user(self, username):
        if username and self.authorizer.has_user(username):
            return self.authorizer.user_table[username]
        else:
            return None

    def get_ip(self, addr):
        return self.ip_table[addr]


class BaseDTPServer(object):
    def __init__(self, host, ip):
        self.ip = ip
        self.queue = Queue()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.bind((host, 0))
        self.sock.listen(5)
        self._ready = False
        self.connected = False
        self.client = None
        self.sock_client = None

    def getsockname(self):
        sockname = self.sock.getsockname()
        result = tuple()
        ip = sockname[0]
        port = sockname[1]
        for p in ip.split('.'):
            result += (int(p),)
        result += (port >> 8,)
        result += (port - (port >> 8 << 8),)
        result = str(result).replace(' ', '')
        return result

    async def run(self, client):
        logger.info("DTP Server listening on {}".format(self.sock.getsockname()))
        self.client = client
        async with self.sock:
            self._ready = True
            client, addr = await self.sock.accept()
            self.sock_client = client
            if addr[0] == self.ip:
                if self.connected:
                    logger.error("DTP Server is already connected.")
                else:
                    self.connected = True
                    logger.info("DTP Server get connection from {}".format(addr))
                    s = client.as_stream()
                    while True:
                        message = await self.queue.get()
                        if message == '\r\n'.encode('utf-8'):
                            await self.client.sendall(parse_message(226, 'Transfer complete.'))
                            break
                        logger.debug("DTP Server get send message.\n{}".format(message))
                        await s.write(message)
            else:
                logger.info("DTP Server refuses connection from {}".format(addr))
        self.connected = False
        self._ready = False
        self.client = None
        self.sock_client = None
        logger.info("DTP Server close connection.")

    async def ready_and_send(self, client):
        logger.debug("DTP Server ready() is called. Ready: {}".format(self._ready))
        while not self._ready:
            logger.debug("Waiting for DTP Server getting ready.")
            await sleep(0.1)
        logger.debug("DTP server is ready.")
        await client.sendall(
            parse_message(227, "Entering passive mode {}.".format(self.getsockname())))

    async def send(self, message):
        logger.debug("DTP Server put message into queue.")
        await self.queue.put(message.encode('utf-8'))

    async def close(self):
        await self.sock.close()
        self.connected = False
        self._ready = False
        self.client = None
        self.sock_client = None
        logger.info("DTP Server close connection.")

    def fileno(self):
        return self.sock.fileno()

    async def sendfile(self, path):
        with open(path, mode='r') as file:
            offset = 0
            blocksize = os.path.getsize(path)
            logger.debug("RETR DTP Server is waiting for writable.")
            while True:
                if self.sock_client:
                    break
                await sleep(1)
            await self.sock_client.writeable()
            logger.debug("RETR DTP Server is writable.")
            while True:
                try:
                    sent = sendfile(self.sock_client.fileno(), file.fileno(), offset, blocksize)
                except BlockingIOError:
                    continue
                logger.debug("RETR DTP Server send {}".format(offset))
                if sent == 0:
                    await self.sock_client.close()
                    await self.client.sendall(parse_message(226, 'Transfer complete.'))
                    await self.close()
                    break
                offset += sent

    async def recv(self):
        while True:
            d = await self.sock_client.recv(1024)
            if not d:
                break
            yield d
