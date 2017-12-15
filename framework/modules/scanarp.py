try:
    from framework.main import ModuleBase, Utils
except ImportError:
    pass

class ArpScan(ModuleBase):
    @property
    def needs_root(self):
        return True  # raw sockets

    @property
    def relative_delay(self):
        return 18

    @property
    def absolute_duration(self):
        # 60 minutes
        return 60 * 60

    @staticmethod
    def build_arp(srcmac, srcip, dstip):
        import struct, socket
        arp = [
            b'\xff\xff\xff\xff\xff\xff',
            bytes(srcmac),
            struct.pack(b'!H', 0x0806),
            struct.pack(b'!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
            struct.pack(b'!H', 0x0001),
            bytes(srcmac),
            socket.inet_aton(srcip),
            b'\x00\x00\x00\x00\x00\x00',
            socket.inet_aton(dstip),
        ]
        return b''.join(arp)

    def arp_request(self, ip, iface):
        import socket
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.bind((iface, socket.SOCK_RAW))
        except Exception as e:
            self.hec_logger(str(e), severity='error')
            raise

        try:
            srcmac = s.getsockname()[4]
            srcip = Utils.iface2ip(iface)
            pkt = self.build_arp(srcmac, srcip, ip)
            s.send(pkt)
        except Exception as e:
            self.hec_logger(str(e), target=ip, severity='error')
            s.close()
            raise
        s.close()

    def do_scan(self):
        import time, random
        sleep_time = 10  ## time between probes
        for iface, net, sn, gw in Utils.routes():
            if gw == '0.0.0.0' and not net.startswith('169.'):
                try:
                    hosts = list(Utils.subnet2list(net, sn))
                    self.hec_logger('ARP scanning range of hosts', start=hosts[0], end=hosts[-1])
                    random.shuffle(hosts)
                    duration = sleep_time * len(hosts)
                    if duration > self.absolute_duration:
                        self.hec_logger('Apprx scan time longer than expected', severity='warning', duration=duration)
                    for host in hosts:
                        self.arp_request(host, iface)
                        time.sleep(sleep_time)
                except:
                    break

    def run(self):
        self.start()
        pid = self.util_childproc(func=self.do_scan)
        self.util_orphanwait(pid)
        self.finish()
