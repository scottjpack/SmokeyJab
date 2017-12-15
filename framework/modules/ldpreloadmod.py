try:
    from framework.main import ModuleBase
except ImportError:
    pass

class LdPreloadMod(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 75

    @property
    def absolute_duration(self):
        return 3600

    def run(self):
        self.start()
        import time
        fname = '/etc/ld.so.preload'
        try:
            with open(fname, 'a+') as f:
                f.seek(0)
                data = f.read()
                f.write('\n# ' + self._banner + '\n')
                offset = f.tell()
            self.hec_logger('Added comment to file', file_path=fname, orig_size=len(data), dorked_size=offset)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        else:
            # Wait one hour before restoring file
            time.sleep(self.absolute_duration)
            with open(fname, 'a+') as f:
                f.truncate(len(data))
            self.hec_logger('Restored contents of the file', file_path=fname, orig_size=len(data), dorked_size=offset)
        self.finish()
