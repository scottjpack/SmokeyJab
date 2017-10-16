try:
    from framework.main import ModuleBase
except ImportError:
    pass

class CrontabEntry(ModuleBase):
    @property
    def relative_delay(self):
        return 80

    @property
    def absolute_duration(self):
        return 3600  # 1 hour

    def run(self):
        self.start()
        import time
        from subprocess import Popen, PIPE
        cmd = '(crontab -l 2>/dev/null; echo "*/5 * * * * /bin/sleep 1  ### {0}") | crontab -'.format(self._banner)
        try:
            Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        else:
            self.hec_logger('Added a crontab entry', command=cmd)
            time.sleep(self.absolute_duration)
            # TODO : remove crontab entry
        self.finish()
