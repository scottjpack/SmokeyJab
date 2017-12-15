try:
    from framework.main import ModuleBase
except ImportError:
    pass


class SetUidOvert(ModuleBase):
    @property
    def relative_delay(self):
        return 40

    @property
    def absolute_duration(self):
        return 24 * 60 * 60  # 1 day

    def run(self):
        self.start()
        import os, stat, shutil, time
        fname = '/tmp/bash'
        shutil.copyfile('/bin/sleep', fname)
        with open(fname, 'a+b') as f:
            f.seek(0, os.SEEK_END)
            f.write(self._banner.encode('utf-8'))
        os.chmod(fname, stat.S_ISUID | stat.S_IRWXU)
        self.hec_logger('Created setuid binary', filename=fname)
        time.sleep(self.absolute_duration)
        os.unlink(fname)
        self.finish()
