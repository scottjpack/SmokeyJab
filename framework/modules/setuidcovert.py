try:
    from framework.main import ModuleBase
except ImportError:
    pass


class SetUidCovert(ModuleBase):
    """ Makes an inconspicuous setuid-root binary in /tmp """
    @property
    def relative_delay(self):
        return 20

    @property
    def absolute_duration(self):
        return 24 * 60 * 60  # 1 day

    def run(self):
        self.start()
        import os, stat, shutil, tempfile, time
        handle, fname = tempfile.mkstemp(suffix='.${FILE_SUFFIX}', prefix='${FILE_PREFIX}-', dir='${DIRECTORY}')
        os.close(handle)
        shutil.copyfile('/bin/sleep', fname)
        with open(fname, 'a+b') as f:
            f.seek(0, os.SEEK_END)
            f.write(self._banner.encode('utf-8'))
        os.chmod(fname, stat.S_ISUID | stat.S_IRWXU)
        self.hec_logger('Created setuid binary', filename=fname)
        time.sleep(self.absolute_duration)
        os.unlink(fname)
        self.finish()
