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

from nmap_scan.NmapScanMethods import NmapScanMethods
from nmap_scan.Scanner import Scanner


class NMAPExecutor:

    def __init__(self, logger, parser, status_builder, nmap_args, scan_tcp=False, scan_udp=False):

        self.__nmap_args = nmap_args
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser

        self.__scan_tcp = scan_tcp
        self.__scan_udp = scan_udp

    def add_args(self):

        if self.__scan_udp:
            self.__parser.add_argument('--not-scan-udp', dest='notscanudp', required=False, action='store_true',
                                       help='Disable UDP scan')
        else:
            self.__parser.add_argument('--scan-udp', dest='scanudp', required=False, action='store_true',
                                       help='Execute UDP scan')
        if self.__scan_tcp:
            self.__parser.add_argument('--not-scan-tcp', dest='notscantcp', required=False, action='store_true',
                                       help='Disable UDP scan')
        else:
            self.__parser.add_argument('--scan-tcp', dest='scantcp', required=False, action='store_true',
                                       help='Execute TCP scan')

    def configure(self, args):

        if self.__scan_tcp:
            if args.notscantcp:
                self.__scan_tcp = False
        else:
            self.__scan_tcp = args.scantcp

        if self.__scan_udp:
            if args.notscanudp:
                self.__scan_udp = False
        else:
            self.__scan_udp = args.scanudp

    def scan(self):

        self.__logger.debug('Perform scan')
        scanner = Scanner(self.__nmap_args)

        if self.__scan_udp:
            scanner.scan_udp_background()

        if self.__scan_tcp:
            scanner.scan_tcp_background()

        scanner.wait_all()

        return scanner.get_report(NmapScanMethods.TCP), scanner.get_report(NmapScanMethods.UDP)
