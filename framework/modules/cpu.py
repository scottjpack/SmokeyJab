try:
    from framework.main import ModuleBase
except:
    pass

class CpuSpike(ModuleBase):
    @property
    def relative_delay(self):
        return 15

    @property
    def absolute_duration(self):
        return 16 * 60  # 16 minutes

    def spike(self):
        import time
        start = time.time()
        while time.time() - start < self.absolute_duration:
            continue
        return

    def run(self):
        self.start()
        pid = self.util_childproc(func=self.spike)
        self.hec_logger('Kicked off CPU-intensive process', pid=pid)
        self.util_orphanwait(pid)
        self.finish()
