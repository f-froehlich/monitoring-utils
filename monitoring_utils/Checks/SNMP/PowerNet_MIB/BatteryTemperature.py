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


from monitoring_utils.Core.Executor.SNMPExecutor import SNMPExecutor
from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Outputs.Perfdata import Perfdata
from monitoring_utils.Core.Plugin.Plugin import Plugin


class BatteryTemperature(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.318.1.1.1.2.2.2'

        Plugin.__init__(self, 'Check the temperature of the battery')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-w', '--warning', dest='warning', required=False,
                                   type=int, help='Warning Temperature', default=25)
        self.__parser.add_argument('-c', '--critical', dest='critical', required=False,
                                   type=int, help='Critical Temperature', default=30)

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__warning = args.warning
        self.__critical = args.critical

    def run(self):
        oids = self.__snmp_executor.run()

        if 1 != len(oids) or '0' != oids[0]['oid']:
            self.__status_builder.unknown(Output(f'Couldn\'t get Battery temperature information'))
            return

        temperature = oids[0]['value']

        output = Output(f'Temperature is {temperature}°',
                        [Perfdata('temperature', temperature, unit='°', warning=self.__warning,
                                  critical=self.__critical, min=0, max=50)])

        if temperature >= self.__critical:
            self.__status_builder.critical(output)
        elif temperature >= self.__warning:
            self.__status_builder.warning(output)
        else:
            self.__status_builder.success(output)
