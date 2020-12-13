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
from monitoring_utils.Checks.NMAP.Scripts.SSLEnumCiphers import SSLEnumCiphers
from monitoring_utils.Core.Executor.NMAPExecutor import NMAPExecutor
from monitoring_utils.Core.Executor.NmapScriptExecutor import NmapScriptExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin
from nmap_scan.NmapArgs import NmapArgs


class Ciphers(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None
        self.__parser = None
        self.__executor = None
        self.__cipher_script = None
        self.__nmapArgs = NmapArgs(scripts=['ssl-enum-ciphers'])
        self.__nmap_script_executor = None

        Plugin.__init__(self, 'Check Ciphers')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__cipher_script = SSLEnumCiphers(self.__logger, self.__status_builder, self.__parser)
        self.__cipher_script.add_args()
        self.__nmapArgs.add_args(self.__parser)
        self.__executor = NMAPExecutor(self.__logger, self.__parser, self.__status_builder,
                                       self.__nmapArgs, scan_tcp=True)
        self.__executor.add_args()

        self.__nmap_script_executor = NmapScriptExecutor(status_builder=self.__status_builder, logger=self.__logger,
                                                         parser=self.__parser)
        self.__nmap_script_executor.add_args()

    def configure(self, args):
        self.__executor.configure(args)
        self.__nmapArgs.configure(args)
        self.__cipher_script.configure(args)
        self.__nmap_script_executor.configure(args)
        self.__nmap_script_executor.add_script('ssl-enum-ciphers', self.__cipher_script)

    def run(self):
        tcp_report, udp_report = self.__executor.scan()
        if None == tcp_report:
            self.__status_builder.unknown('No TCP scan was executed, pass --scan-tcp to proceed')
            return

        self.__nmap_script_executor.execute(tcp_report)

        self.__status_builder.success('All checks passed')
