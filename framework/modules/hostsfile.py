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
        return 40

    @property
    def absolute_duration(self):
        return 3600  # 1 hour

    def run(self):
        self.start()
        import time
        hostname = 'yourfriendlyred.team'
        with open('/etc/hosts', 'a+') as f:
            f.seek(0)
            data = f.read()
            f.write('\n127.31.3.37\t{0}\n'.format(hostname))
        self.hec_logger('Added a new host to /etc/hosts', hostname=hostname)
        time.sleep(self.absolute_duration)
        with open('/etc/hosts', 'a+') as f:
            f.truncate(len(data))
        self.hec_logger('Removed entry from hosts file', hostname=hostname)
        self.finish()
