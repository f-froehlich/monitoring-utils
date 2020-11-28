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


from monitoring_utils.Core.Executor.NMAPExecutor import NMAPExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class OpenPorts(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None
        self.__parser = None
        self.__executor = None

        self.__expected = None
        self.__host = None
        self.__allowed_ports = []

        Plugin.__init__(self, 'Check DNSSEC status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__executor = NMAPExecutor(self.__logger, self.__parser, self.__status_builder)
        self.__executor.add_args()

        self.__parser.add_argument('-a', '--allowed-port', dest='allowedports', action='append',
                                   help='Allowed open ports. Format: PORT/udp | PORT/tcp', default=[])

    def configure(self, args):
        self.__executor.configure(args)
        self.__allowed_ports = args.allowedports

    def run(self):

        self.check_ports()
        self.__status_builder.success('All checks passed')

    def check_ports(self):
        report, runtime, stats = self.__executor.scan()
        print(report)
        print(runtime)
        print(stats)
        if None == report:
            return

        open_ports = []
        for port_report in report:
            if port_report['state'] == 'open':
                port_config = port_report['portid'] + '/' + port_report['protocol']
                open_ports.append(port_config)
                if port_config not in self.__allowed_ports:
                    self.__status_builder.critical('Port "' + port_config + "' is open but should be closed")

        for port_config in self.__allowed_ports:
            if port_config not in open_ports:
                self.__status_builder.warning('Port "' + port_config + "' is closed but should be open")
