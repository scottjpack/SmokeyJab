try:
    from framework.main import ModuleBase
except ImportError:
    pass

class UserGroupPrivs(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 50

    @property
    def absolute_duration(self):
        return 24 * 3600  # 1 day

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

    def run(self):
        self.start()
        import time, pwd
        from subprocess import check_call, PIPE
        username = '${USER_NAME}'
        should_del_user = False
        try:
            pwd.getpwnam(username)
        except KeyError:
            self.hec_logger('User does not exist, attempting to add to the system', severity='warning', username=username)
            try:
                self.create_user(username)
                should_del_user = True
            except Exception as e:
                self.hec_logger(str(e), severity='error')
                self.finish()
                return
        cmd = 'usermod -a -G wheel {0}'.format(username)
        try:
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Added user to a privileged group', username=username, group='wheel')
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            self.finish()
            return
        time.sleep(self.absolute_duration)
        try:
            cmd = 'gpasswd -d {0} wheel'.format(username)
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Removed a user from privileged group', username=username, groupname='wheel')
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        if should_del_user:
            self.hec_logger('Attempting to delete user', username=username)
            try:
                self.remove_user(username)
            except Exception as e:
                self.hec_logger(str(e), severity='error', username=username)
        self.finish()


