try:
    from framework.main import ModuleBase
except ImportError:
    pass

class NewProc(ModuleBase):
    @property
    def relative_delay(self):
        return 15

    @property
    def absolute_duration(self):
        return 16 * 60  # 16 minutes

    def run(self):
        self.start()
        import time, os, signal
        pid = self.util_childproc(fname='/bin/bash', args=('/bin/sleep',))
        self.hec_logger('New process spawned', pid=pid, exe='/bin/bash', cmdline='/bin/sleep')
        time.sleep(self.absolute_duration)
        try:
            os.kill(pid, signal.SIGKILL)
            self.hec_logger('Killed child process', pid=pid)
        except Exception as e:
            self.hec_logger('Couldn\'t kill child process: ' + str(e))
        self.util_orphanwait(pid)
        self.finish()
