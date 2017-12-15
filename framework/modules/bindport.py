try:
    from framework.main import ModuleBase
except ImportError:
    pass


class BindPort(ModuleBase):
    @property
    def relative_delay(self):
        return 90

    @property
    def absolute_duration(self):
        # 60 minutes
        return 60 * 60

    def bind_port(self, port):
        import socket, time
        s = socket.socket()
        s.bind(('', port))
        s.listen(1)
        time.sleep(self.absolute_duration)
        return

    def run(self):
        self.start()
        port = int('${PORT}')
        pid = self.util_childproc(func=self.bind_port, args=(port,))
        self.hec_logger('Kicked off process to listen on a port', pid=pid, port=port)
        self.util_orphanwait(pid)
        self.finish()
