try:
    from framework.main import ModuleBase
except ImportError:
    pass


class BindPort(ModuleBase):
    @property
    def relative_delay(self):
        return 60

    @property
    def absolute_duration(self):
        # 16 minutes
        return 16*60

    def bind_port(self):
        import socket, time
        s = socket.socket()
        s.bind(('', 8888))
        s.listen(1)
        time.sleep(self.absolute_duration)
        return

    def run(self):
        self.start()
        pid = self.util_childproc(func=self.bind_port)
        self.hec_logger('Kicked off process to listen on a port', pid=pid, port=8888)
        self.util_orphanwait(pid)
        self.finish()
