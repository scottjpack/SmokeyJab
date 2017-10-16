try:
    from framework.main import ModuleBase
except ImportError:
    pass

class SetUid(ModuleBase):
    @property
    def relative_delay(self):
        return 95

    @property
    def absolute_duration(self):
        return 24 * 3600  # 1 day

    def run(self):
        self.start()
        import os, stat, shutil, tempfile, time
        handle, fname = tempfile.mkstemp(suffix='.dat', prefix='yumlock-', dir='/tmp')
        os.close(handle)
        shutil.copyfile('/bin/sleep', fname)
        with open(fname, 'ab+') as f:
            f.write(self._banner.encode('utf-8'))
        os.chmod(fname, stat.S_ISUID | stat.S_IRWXU)
        self.hec_logger('Created setuid binary', filename=fname)
        time.sleep(self.absolute_duration)
        # TODO : clean up the suid binary!!
        self.finish()
