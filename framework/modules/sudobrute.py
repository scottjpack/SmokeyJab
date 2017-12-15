try:
    from framework.main import ModuleBase
except ImportError:
    pass

class SudoBrute(ModuleBase):
    @property
    def needs_root(self):
        return False

    @property
    def relative_delay(self):
        # On a scale of 1 (least) to 100 (most) likely to get caught
        return 95

    @property
    def absolute_duration(self):
        return 60

    def create_user(self, user):
        from subprocess import check_call, PIPE
        cmd = 'useradd -m -c "{1}" -l -N -s /bin/false {0}'.format(user, self._banner.replace(':',''))
        try:
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Added a user', username=user)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            raise

    def remove_user(self, user):
        from subprocess import check_call, PIPE
        cmd = 'userdel -r {0}'.format(user)
        try:
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Removed a user', username=user)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            raise

    def do_sudo(self, low_user=None):
        import os, subprocess, pwd
        passwords = ['password0', 'password1', 'password2', 'password3', 'password4', 'password5', 'password6',
                     'password7', 'password8', 'password9']
        self.hec_logger('Current privileges', uid=os.getuid(), euid=os.geteuid())
        if os.geteuid() == 0:
            # drop privs. run in a child process to avoid breaking the framework!
            try:
                assert os.name == 'posix'
                import pwd
                pw = pwd.getpwnam(low_user)
                uid = pw.pw_uid
                os.setreuid(uid, uid)
                self.hec_logger('Dropped privs', uid=os.getuid(), euid=os.geteuid())
            except Exception as e:
                self.hec_logger('Error occured while dropping privs', error=str(e), severity='error')
                return
        for password in passwords:
            try:
                subprocess.check_call('echo {0} | sudo -Sk /bin/bash -c "true"'.format(password), shell=True)
            except:
                pass  ## expected that the call should fail
            else:
                self.hec_logger('Weak password detected', password=password, severity='warning')
                continue

    def run(self):
        import pwd
        self.start()
        user = '${LOW_USER}'
        should_delete_user = False
        try:
            pwd.getpwnam(user)
        except KeyError:
            self.hec_logger('User does not exist, adding it', username=user)
            try:
                self.create_user(user)
                should_delete_user = True
            except Exception as e:
                self.hec_logger(str(e), severity='error', username=user)
                return
        pid = self.util_childproc(func=self.do_sudo, args=(user,))
        self.util_orphanwait(pid)
        if should_delete_user:
            self.hec_logger('Attempting to delete user', username=user)
            try:
                self.remove_user(user)
            except Exception as e:
                self.hec_logger(str(e), username=user, severity='error')
        self.finish()
