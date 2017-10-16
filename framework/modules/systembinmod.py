try:
    from framework.main import ModuleBase
except ImportError:
    pass

class SshMod(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 75

    @property
    def absolute_duration(self):
        return 5 * 3600

    def run(self):
        self.start()
        import shutil, time
        from hashlib import md5
        bin_file = '/usr/bin/ssh'
        backup = bin_file + '.bak'
        shutil.copy(bin_file, backup)
        shutil.copystat(bin_file, backup)
        with open(bin_file, 'rb') as source:
            with open(backup, 'rb') as dest:
                backup_succeeded = (md5(source.read()).digest() == md5(dest.read()).digest())
                self.hec_logger('Backed up system file', src_fname=bin_file, dst_fname=backup, success=backup_succeeded)
        if backup_succeeded:
            with open(bin_file, 'ab') as f:
                f.write('\n'+self._banner+'\n')
                self.hec_logger('Dorked system file', filename=bin_file)
            shutil.copystat(backup, bin_file)
            time.sleep(self.absolute_duration)
            shutil.move(backup, bin_file)
            self.hec_logger('Backup restored', src_fname=backup, dst_fname=bin_file)
        else:
            self.hec_logger('Backup failed, bailing', severity='warning')
        self.finish()
