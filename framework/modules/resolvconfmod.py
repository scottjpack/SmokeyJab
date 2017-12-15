try:
    from framework.main import ModuleBase
except ImportError:
    pass

class DnsServer(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 85

    @property
    def absolute_duration(self):
        return 3600  # 1 hour

    def run(self):
        self.start()
        import time
        nameserver = '${NAMESERVER}'
        with open('/etc/resolv.conf', 'a+') as f:
            f.seek(0)
            data = f.read()
            f.write('\nnameserver {0}  # {1}\n'.format(nameserver, self._banner))
            offset = f.tell()
        self.hec_logger('Added a nameserver to /etc/resolv.conf', server=nameserver)
        time.sleep(self.absolute_duration)
        with open('/etc/resolv.conf', 'a+') as f:
            f.truncate(len(data))
        self.hec_logger('Restored contents of /etc/resolv.conf', orig_size=len(data), dorked_size=offset)
        self.finish()
