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


class Load(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.2021.10.1'

        Plugin.__init__(self, 'Check CPU Load average')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-w', '--warning', dest='warning', required=False,
                                   type=str, help='Warning load. Format: LOAD1,LOAD5,LOAD15')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=False,
                                   type=str, help='Critical load. Format: LOAD1,LOAD5,LOAD15')

    def configure(self, args):
        self.__snmp_executor.configure(args)

        warning = args.warning
        if None is not warning:
            warning = warning.split(',')
            if len(warning) != 3:
                self.__status_builder.unknown(
                    Output('Format for warning load mismatch. Expected Format: LOAD1,LOAD5,LOAD15'))
                self.__status_builder.exit()
            self.__warning = [float(warning[0]), float(warning[1]), float(warning[2])]

        critical = args.critical
        if None is not critical:
            critical = critical.split(',')
            if len(critical) != 3:
                self.__status_builder.unknown(
                    Output('Format for critical load mismatch. Expected Format: LOAD1,LOAD5,LOAD15'))
                self.__status_builder.exit()
            self.__critical = [float(critical[0]), float(critical[1]), float(critical[2])]

        if None is self.__warning and self.__critical is not None:
            self.__status_builder.unknown(Output('If critical load is defined, you have to set warning load'))
            self.__status_builder.exit()

        if None is not self.__warning and self.__critical is None:
            self.__status_builder.unknown(Output('If warning load is defined, you have to set critical load'))
            self.__status_builder.exit()

    def run(self):
        oids = self.__snmp_executor.run()

        status_data = {
            1: {},
            2: {},
            3: {}
        }

        keys = {
            '2': 'name',
            '3': 'load',
            '4': 'configuredError',
            '5': 'loadInt',
            '6': 'loadFloat',
            '100': 'error',
            '101': 'errorMessage',
        }
        for oid in oids:
            base = oid['oid'].split('.')

            id = int(base[1])

            if base[0] == '1':
                continue

            status_data[id][keys.get(base[0])] = oid['value']

        for status_data_id in status_data:
            data = status_data[status_data_id]
            index = status_data_id - 1

            perfdata = [
                Perfdata(f'load', data['loadFloat'], warning=self.__warning[index], critical=self.__critical[index]),
            ]

            if 0 != data['error']:
                output = Output(
                    f'Load \"{data["name"]}\" Got an unexpected error "{data["errorMessage"]}" (code {data["swapError"]})',
                    perfdata
                )
                self.__status_builder.critical(output)
                continue

            output = Output(
                f"Disk load \"{data['name']}\"",
                perfdata
            )

            if None is self.__warning:
                self.__status_builder.success(output)
            else:
                if self.__critical[index] <= data['loadFloat']:
                    self.__status_builder.critical(output)
                elif self.__warning[index] <= data['loadFloat']:
                    self.__status_builder.warning(output)
                else:
                    self.__status_builder.success(output)
