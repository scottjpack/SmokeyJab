try:
    from framework.main import ModuleBase, Utils
except ImportError:
    pass

class ExternalDCExternalProductScan(ModuleBase):
    @property
    def needs_root(self):
        return False

    @property
    def relative_delay(self):
        return 98

    @property
    def absolute_duration(self):
        return 2560

    def do_scan(self):
        import socket, random
        ports = [21, 22, 23, 80, 443]
        timeout = 2  # time to wait on dropped packets
        try:
            ip, cidr = '${TARGET_CIDR}'.split('/')
            hosts = list(Utils.cidr2list(ip, int(cidr)))
            self.hec_logger('Port scanning hosts in subnet', size=len(hosts), start=hosts[0], end=hosts[-1])
            random.shuffle(hosts)
            duration = timeout * len(hosts) * len(ports)
            if duration > self.absolute_duration:
                self.hec_logger('Apprx scan time longer than expected', severity='warning', duration=duration)
            for host in hosts:
                for port in ports:
                    s = socket.socket()
                    s.settimeout(timeout)
                    try:
                        s.connect((host, port))
                    except (socket.timeout, socket.error):
                        s.close()
                        continue
                    except Exception as e:
                        self.hec_logger(str(e), target=host, severity='error')
                        raise
                    else:
                        s.shutdown(socket.SHUT_RDWR)
                    s.close()
        except Exception as e:
            self.hec_logger('Fatal socket error [{0}]'.format(e), severity='error')
            return

    def run(self):
        self.start()
        pid = self.util_childproc(func=self.do_scan)
        self.util_orphanwait(pid)
        self.finish()
