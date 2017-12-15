try:
    from framework.main import ModuleBase
except ImportError:
    pass

class RcFileModOvert(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 95

    @property
    def absolute_duration(self):
        return 60 * 60

    def run(self):
        self.start()
        import time
        try:
            with open('/etc/rc.local', 'a+') as f:
                f.seek(0)
                data = f.read()
                f.write('\n# ' + self._banner + '\n')
                offset = f.tell()
            self.hec_logger('Added content to the file', file_path='/etc/rc.local')
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        else:
            # Wait one hour before restoring file
            time.sleep(self.absolute_duration)
            with open('/etc/rc.local', 'a+') as f:
                f.truncate(len(data))
            self.hec_logger('Restored contents of the file', file_path='/etc/rc.local', orig_size=len(data),
                            dorked_size=offset)
        self.finish()
