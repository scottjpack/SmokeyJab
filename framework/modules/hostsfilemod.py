try:
    from framework.main import ModuleBase
except ImportError:
    pass

class HostsFile(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        # On a scale of 1 (least) to 100 (most) likely to get caught
        return 85

    @property
    def absolute_duration(self):
        return 60 * 60  # 1 hour

    def run(self):
        self.start()
        import time
        hostname = '${HOSTNAME}'
        ip_addr = '${IP_ADDR}'
        with open('/etc/hosts', 'a+') as f:
            f.seek(0)
            data = f.read()
            f.write('\n{1}\t{0} # {2}\n'.format(hostname, ip_addr, self._banner))
        self.hec_logger('Added a new host to /etc/hosts', hostname=hostname, ip_addr=ip_addr)
        time.sleep(self.absolute_duration)
        with open('/etc/hosts', 'a+') as f:
            f.truncate(len(data))
        self.hec_logger('Removed entry from hosts file', hostname=hostname, ip_addr=ip_addr)
        self.finish()