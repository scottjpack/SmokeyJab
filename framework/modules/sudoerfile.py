try:
    from framework.main import ModuleBase
except ImportError:
    pass

class UserAddSudoers(ModuleBase):
    """ creates a sudoers.d file for the user """
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 80

    @property
    def absolute_duration(self):
        return 24 * 60 * 60  # 1 day

    def run(self):
        self.start()
        import os, stat, time
        username = '${USER_NAME}'
        fname = '/etc/sudoers.d/${SUDOERS_FNAME}~'
        try:
            if not os.path.exists('/etc/sudoers.d'):
                os.mkdir('/etc/sudoers.d', mode=0o755)
            if not os.path.exists('/etc/sudoers.d') or not os.path.isdir('/etc/sudoers.d'):
                self.hec_logger('Error: /etc/sudoers.d directory does not exist!', severity='error')
                self.finish()
                return
            with open(fname, 'w+') as f:
                f.write('{0} ALL=(ALL:ALL) ALL'.format(username))
            os.chmod(fname, stat.S_IRUSR | stat.S_IRGRP)
            self.hec_logger('Created a sudoers.d file', username=username, fname=fname)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            self.finish()
            return
        time.sleep(self.absolute_duration)
        try:
            os.unlink(fname)
            self.hec_logger('Removed sudoers.d file', username=username, fname=fname)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        self.finish()
