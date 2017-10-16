try:
    from framework.main import ModuleBase
except ImportError:
    pass

class PyLibModify(ModuleBase):
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
        import inspect, time
        try:
            import requests
        except:
            self.hec_logger('Requests package is not available', severity='error')
        else:
            req_path = inspect.getsourcefile(requests)
            self.hec_logger('Appending data to requests library', filename=req_path)
            try:
                with open(req_path, 'a+') as f:
                    f.seek(0)
                    data = f.read()
                    f.write('\n# ' + self._banner)
                    offset = f.tell()
                self.hec_logger('Appended data to requests library', filename=req_path)
                # Wait an hour before restoring file contents
                time.sleep(self.absolute_duration)
                with open(req_path, 'a') as f:
                    f.truncate(len(data))
                self.hec_logger('Restored contents of requests library', orig_size=len(data), dorked_size=offset)
            except Exception as e:
                self.hec_logger(str(e), severity='error')
        self.finish()
