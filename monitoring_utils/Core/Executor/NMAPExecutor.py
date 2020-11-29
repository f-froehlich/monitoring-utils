#!/usr/bin/python3
# -*- coding: utf-8

#  Monitoring monitoring-utils
#
#  Monitoring monitoring-utils are the background magic for my plugins, scripts and more
#
#  Copyright (c) 2020 Fabian Fröhlich <mail@confgen.org> <https://icinga2.confgen.org>
#
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  For all license terms see README.md and LICENSE Files in root directory of this Project.
#
#  Checkout this project on github <https://github.com/f-froehlich/monitoring-utils>
#  and also my other projects <https://github.com/f-froehlich>
import traceback

import nmap3


class NMAPExecutor:

    def __init__(self, logger, parser, status_builder, host=None, top_ports=None, only_tcp=False, only_udp=False,
                 ports=None, pn=False, min_rate=None, max_rate=None, host_timeout=None, max_retries=None, fast=False,
                 scripts=[]
                 ):

        self.__open_ports = []
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser

        self.__host = host
        self.__top_ports = top_ports
        self.__only_tcp = only_tcp
        self.__only_udp = only_udp
        self.__ports = ports
        self.__pn = pn
        self.__minrate = min_rate
        self.__maxrate = max_rate
        self.__hosttimeout = host_timeout
        self.__maxretries = max_retries
        self.__fast = fast
        self.__scripts = scripts

    def add_args(self):
        self.__parser.add_argument('-H', '--host', dest='host', required=True, default=self.__host,
                                   help='Host to scan')

        self.__parser.add_argument('--top-ports', dest='topports', required=False, default=self.__top_ports, type=int,
                                   help='Scan top ports')

        self.__parser.add_argument('--ports', dest='ports', required=False, default=self.__ports, type=str,
                                   help='Ports to scan e.g. U:53,111,137,T:21-25,80,139,8080,S:9')

        self.__parser.add_argument('--min-rate', dest='minrate', required=False, default=self.__minrate, type=int,
                                   help='Send packets no slower than <number> per second')
        self.__parser.add_argument('--max-rate', dest='maxrate', required=False, default=self.__maxrate, type=int,
                                   help='Send packets no faster than <number> per second')
        self.__parser.add_argument('--host-timeout', dest='hosttimeout', required=False, default=self.__hosttimeout,
                                   type=int, help='Give up on target after this long')
        self.__parser.add_argument('--max-retries', dest='maxretries', required=False, default=self.__maxretries,
                                   type=int, help='Caps number of port scan probe retransmissions.')

        self.__parser.add_argument('--script', dest='scripts', action='append', default=self.__scripts,
                                   help='Scripts to run during scan')

        if self.__only_udp:
            self.__parser.add_argument('--not-only-udp', dest='notonlyudp', required=False, action='store_true',
                                       help='Disable only execute UDP scan')
        else:
            self.__parser.add_argument('--only-udp', dest='onlyudp', required=False, action='store_true',
                                       help='Only execute UDP scan')

        if self.__only_tcp:
            self.__parser.add_argument('--not-only-tcp', dest='notonlytcp', required=False, action='store_true',
                                       help='Disable only execute UDP scan')
        else:
            self.__parser.add_argument('--only-tcp', dest='onlytcp', required=False, action='store_true',
                                       help='Only execute TCP scan')

        if self.__pn:
            self.__parser.add_argument('-not-pn', dest='notpn', required=False, action='store_true',
                                       help='Not treat all hosts as online - enable host discovery')
        else:
            self.__parser.add_argument('--pn', dest='pn', required=False, action='store_true',
                                       help='Treat all hosts as online - skip host discovery')

        if self.__fast:
            self.__parser.add_argument('--not-fast', dest='notfast', required=False, action='store_true',
                                       help='Disable Fast mode')
        else:
            self.__parser.add_argument('--fast', dest='fast', required=False, action='store_true',
                                       help='Fast mode - Scan fewer ports than the default scan.')

    def configure(self, args):
        self.__host = args.host
        self.__top_ports = args.topports
        self.__ports = args.ports
        self.__minrate = args.minrate
        self.__maxrate = args.maxrate
        self.__hosttimeout = args.hosttimeout
        self.__maxretries = args.maxretries
        self.__scripts = args.scripts

        if self.__fast:
            if args.notfast:
                self.__fast = False
        else:
            self.__fast = args.fast

        if self.__only_tcp:
            if args.notonlytcp:
                self.__only_tcp = False
        else:
            self.__only_tcp = args.onlytcp

        if self.__only_udp:
            if args.notonlyudp:
                self.__only_udp = False
        else:
            self.__only_udp = args.onlyudp

        if self.__pn:
            if args.notpn:
                self.__pn = False
        else:
            self.__pn = args.pn

        if '/' in self.__host or '-' in self.__host:
            self.__status_builder.unknown('Can only scan single host but net was given.')
            self.__status_builder.exit()
        if self.__only_tcp and self.__only_udp:
            self.__status_builder.unknown('Can only set --only-tcp or --only-udp')
            self.__status_builder.exit()

    def filter_open_ports(self, report):
        for port_report in report:
            if port_report['state'] == 'open':
                self.__open_ports.append(port_report)

    def get_open_ports(self):
        return self.__open_ports

    def scan(self):

        if None != self.__top_ports:
            return self.scan_top_ports()

        elif None != self.__ports:
            return self.scan_custom_ports()

        else:
            return self.scan_default()

    def scan_default(self):
        self.__logger.info('Scanning default ports of host "' + self.__host + '".')
        return self.combined_scan()

    def scan_top_ports(self):
        self.__logger.info('Scanning top ports ' + str(self.__top_ports) + ' of host "' + self.__host + '".')
        return self.combined_scan()

    def scan_custom_ports(self):
        self.__logger.info('Scanning custom ports ' + str(self.__ports) + ' of host "' + self.__host + '".')
        return self.combined_scan()

    def combined_scan(self):
        self.__logger.debug('Perform combined scan')
        if not self.__only_udp:
            tcp_host_result, tcp_runtime, tcp_stats = self.scan_tcp()
            if None == tcp_host_result:
                return tcp_host_result, tcp_runtime, tcp_stats
        else:
            tcp_host_result, tcp_runtime, tcp_stats = [], [], []

        if not self.__only_tcp:
            udp_host_result, udp_runtime, udp_stats = self.scan_udp()
            if None == udp_host_result:
                return udp_host_result, udp_runtime, udp_stats
        else:
            udp_host_result, udp_runtime, udp_stats = [], [], []

        result = tcp_host_result + udp_host_result
        self.filter_open_ports(result)
        return result, tcp_runtime + udp_runtime, tcp_stats + udp_stats

    def parse_report(self, result):

        self.__logger.debug(result['runtime'])
        self.__logger.debug(result['stats'])

        host_result = result.get(self.__host, None)
        if None == host_result:
            self.__logger.debug('No scan report for host "' + self.__host + '" found.')
            self.__status_builder.unknown('No scan report for host "' + self.__host + '" found.')
            return None, [result['runtime']], [result['stats']]
        self.__logger.debug('Found scan report for host "' + self.__host + '".')

        return host_result, [result['runtime']], [result['stats']]

    def get_args(self):
        self.__logger.info('Parsing args')

        default_args = ''
        for script in self.__scripts:
            self.__logger.debug('Add script "' + script + '"')
            default_args += ' --script ' + script

        if None != self.__pn:
            self.__logger.debug('Setup -Pn')
            default_args += ' -Pn'

        if None != self.__minrate:
            self.__logger.debug('Setup --min-rate to "' + self.__minrate + '"')
            default_args += ' --min-rate ' + self.__minrate

        if None != self.__maxrate:
            self.__logger.debug('Setup --max-rate to "' + self.__maxrate + '"')
            default_args += ' --max-rate ' + self.__maxrate

        if None != self.__hosttimeout:
            self.__logger.debug('Setup --host-timeout to "' + self.__hosttimeout + '"')
            default_args += ' --host-timeout ' + self.__hosttimeout

        if None != self.__hosttimeout:
            self.__logger.debug('Setup --max-retries to "' + self.__maxretries + '"')
            default_args += ' --max-retries ' + self.__maxretries

        if None != self.__top_ports:
            self.__logger.debug('Setup --top-ports to "' + str(self.__top_ports) + '"')
            return ' --top-ports ' + str(self.__top_ports) + default_args
        if None != self.__ports:
            self.__logger.debug('Setup -p to "' + str(self.__ports) + '"')
            return ' -p ' + str(self.__ports) + default_args

        # default scan
        if None != self.__fast:
            self.__logger.debug('Setup -F')
            default_args += ' -F'

        return default_args

    def scan_tcp(self):
        self.__logger.info('Perform TCP scan to host "' + self.__host + '"')
        nmap = nmap3.NmapScanTechniques()
        try:
            report = nmap.nmap_tcp_scan(self.__host, self.get_args())
        except Exception as e:
            self.__logger.info('Exception occurred during nmap call')
            self.__logger.debug(traceback.format_exc())
            self.__status_builder.unknown('Exception occurred during nmap call:\n' + str(e))
            self.__status_builder.exit()

        self.__logger.info('TCP scan finished. Summary: "' + report['runtime']['summary'] + '"')
        self.__logger.debug(report)

        return self.parse_report(report)

    def scan_udp(self):
        self.__logger.info('Perform UDP scan to host "' + self.__host + '"')
        nmap = nmap3.NmapScanTechniques()
        try:
            report = nmap.nmap_udp_scan(self.__host, self.get_args())
        except Exception as e:
            self.__logger.info('Exception occurred during nmap call')
            self.__logger.debug(traceback.format_exc())
            self.__status_builder.unknown('Exception occurred during nmap call:\n' + str(e))
            self.__status_builder.exit()

        self.__logger.info('UDP scan finished. Summary: "' + report['runtime']['summary'] + '"')
        self.__logger.debug(report)

        return self.parse_report(report)
