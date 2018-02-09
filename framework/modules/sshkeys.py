try:
    from framework.main import ModuleBase
except ImportError:
    pass

class SshKeys(ModuleBase):
    @property
    def relative_delay(self):
        # On a scale of 1 (least) to 100 (most) likely to get caught
        return 15

    @property
    def absolute_duration(self):
        return 24 * 60 * 60  # 1 day

    def run(self):
        self.start()
        import os, subprocess, shlex, time
        ssh_dir = os.path.join(os.path.expanduser('~'), '.ssh')
        if not os.path.isdir(ssh_dir):
            os.mkdir(ssh_dir)
        key_name = os.path.join(ssh_dir, '${KEY_FILENAME}')
        auth_keys = os.path.join(ssh_dir, 'authorized_keys')
        while os.path.isfile(key_name):
            key_name += 'x'
        command = 'ssh-keygen -f {0} -t rsa -b 1024 -P "jAb2R1C8HsTiXCoB" -C "{1}"'.format(key_name, self._banner)
        try:
            subprocess.call(shlex.split(command.encode()))
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        else:
            self.hec_logger('Created SSH keys', pubkey=key_name+'.pub', privkey=key_name)
            with open(key_name+'.pub') as f:
                pubkey = f.read()
            with open(auth_keys, 'a+') as f:
                f.seek(0)
                data = f.read()
                f.write('\n' + pubkey + '\n')
                offset = f.tell()
            self.hec_logger('Added public key to authorized_keys file', authkey_filename=auth_keys, comment=self._banner)
            time.sleep(self.absolute_duration)
            with open(auth_keys, 'a+') as f:
                f.truncate(len(data))
            self.hec_logger('Restored contents of authorized_keys',
                            orig_size=len(data), dorked_size=offset, authkey_filename=auth_keys)
            os.unlink(key_name)
            os.unlink(key_name+'.pub')
            self.hec_logger('Removed SSH keys', pubkey=key_name + '.pub', privkey=key_name)
        self.finish()
