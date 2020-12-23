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
from argparse import ArgumentError

from monitoring_utils.Core.Executor.NMAPExecutor import NMAPExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin
from nmap_scan.NmapArgs import NmapArgs


class OpenPorts(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None
        self.__parser = None
        self.__executor = None

        self.__single_host = False
        self.__expected = None
        self.__host = None
        self.__nmapArgs = NmapArgs()
        self.__allowed_ports = {}
        self.__config_for_proto = {'tcp': False, 'udp': False}

        Plugin.__init__(self, 'Check DNSSEC status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__executor = NMAPExecutor(self.__logger, self.__parser, self.__status_builder, self.__nmapArgs,
                                       scan_tcp=True, scan_udp=True)
        self.__executor.add_args()
        self.__nmapArgs.add_args(self.__parser)

        self.__parser.add_argument('-a', '--allowed-port', dest='allowedports', action='append',
                                   help='Allowed open ports. Format: HOST/PORT/udp | HOST/PORT/tcp '
                                        'or PORT/udp | PORT/tcp if --single-host is set', default=[])
        try:
            self.__parser.add_argument('--single-host', dest='singlehost', action='store_true',
                                       help='Only test a single host. If set you don\'t have to add "HOST/" on all other '
                                            'parameters')
        except ArgumentError:
            pass

    def configure(self, args):
        self.__executor.configure(args)
        self.__nmapArgs.configure(args)
        self.__single_host = args.singlehost

        if self.__single_host:
            if len(args.hosts) != 1:
                self.__status_builder.unknown('You set --single-host but you don\'t set exactly once --host. Can\'t '
                                              'proceed with this configuration.')
                self.__status_builder.exit()

        for config in args.allowedports:
            self.__logger.debug('Parsing config "{config}"'.format(config=config))

            if self.__single_host:
                host = args.hosts[0]
                config = host + '/' + config

            config_array = config.split('/')
            if len(config_array) != 3 or config_array[2] not in ['udp', 'tcp']:
                self.__status_builder.unknown('Invalid config "{config}" detected'.format(config=config))
                continue

            new_config = self.__allowed_ports.get(config[0], {'tcp': [], 'udp': []})
            new_config[config_array[2]].append(int(config_array[1]))
            self.__allowed_ports[config_array[0]] = new_config
            self.__config_for_proto[config_array[2]] = True

    def run(self):

        self.check_ports()
        self.__status_builder.success('All checks passed')

    def check_ports(self):
        tcp_report, udp_report = self.__executor.scan()

        if None != tcp_report:
            self.check_report(tcp_report, 'tcp')
        elif self.__config_for_proto['udp']:
            self.__status_builder.unknown(
                'No TCP scan executed but TCP ports configured, pass --scan-tcp to execute it.')

        if None != udp_report:
            self.check_report(udp_report, 'udp')
        elif self.__config_for_proto['udp']:
            self.__status_builder.unknown(
                'No UDP scan executed but UDP ports configured, pass --scan-udp to execute it.')

        if None == tcp_report and None == udp_report:
            self.__status_builder.unknown('No scan executed, pass --scan-tcp and / or --scan-udp')

    def check_report(self, report, proto):
        used_ips = []

        for host in report.get_hosts():
            allowed_ports = []
            ips = []
            for address in host.get_addresses():
                if address.is_ip():
                    ips.append(address.get_addr())
                    allowed_ports += self.__allowed_ports.get(address.get_addr(), {'tcp': [], 'udp': []})[proto]
            used_ips += ips

            open_ports = []
            for port in host.get_open_ports():
                if port.get_port() not in allowed_ports:
                    self.__status_builder.critical(
                        'Port "{port}/{proto}" is open on host with ips "{ip}" but should be closed'
                            .format(port=port.get_port(), ip='", " '.join(ips), proto=proto))
                open_ports.append(port.get_port())

            for port in allowed_ports:
                if port not in open_ports:
                    self.__status_builder.warning(
                        'Port "{port}/{proto}" is closed but should be open on host with ips "{ip}"'
                            .format(port=port, ip='", " '.join(ips), proto=proto)
                    )

        for ip in self.__allowed_ports:
            if ip not in used_ips and 0 != len(self.__allowed_ports[ip][proto]):
                self.__status_builder.warning(
                    'No Report for host with ip "{ip}" and proto "{proto}" found'
                        .format(ip=ip, proto=proto)
                )
