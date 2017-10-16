try:
    from framework.main import ModuleBase
except ImportError:
    pass


class NetworkConnections(ModuleBase):
    @property
    def relative_delay(self):
        return 10

    @property
    def absolute_duration(self):
        return 16 * 60  # 16 minutes

    def run(self):
        self.start()
        import select
        import time
        start = time.time()
        host = ('${NETCONNECT_HOST}', int('${NETCONNECT_PORT}'))
        self.hec_logger('Maintaining network connection', remote_host='{0}:{1}'.format(*host))
        while True:
            if time.time() - start > self.absolute_duration:
                break
            s = self.util_netconnect(host, timeout=60)
            select.select([s], [], [], 61)
            s.close()
            time.sleep(1)
        self.finish()
