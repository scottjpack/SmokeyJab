try:
    from framework.main import ModuleBase
except ImportError:
    pass

class IptablesRule(ModuleBase):
    @property
    def needs_root(self):
        return True

    @property
    def relative_delay(self):
        return 45

    @property
    def absolute_duration(self):
        return 24 * 3600  # 1 hour

    def run(self):
        self.start()
        import time
        from subprocess import check_call, PIPE
        cmd_template = 'iptables -t nat -{0} OUTPUT -p tcp --dport ${DEST_PORT} -d ${DEST_HOST} -m comment --comment "{1}" -j DNAT --to-destination ${DNAT_HOST}:${DNAT_PORT}'
        try:
            cmd = cmd_template.format('I', self._banner)
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Adding an iptables rule to simulate outbound connection masking', command=cmd)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            self.finish()
            return
        time.sleep(self.absolute_duration)
        try:
            cmd = cmd_template.format('D', self._banner)
            check_call(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            self.hec_logger('Removed iptables rule', command=cmd)
        except Exception as e:
            self.hec_logger(str(e), severity='error')
        self.finish()
