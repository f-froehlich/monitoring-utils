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


class StorageIO(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__disk_id = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.6574.101.1.1'

        Plugin.__init__(self, 'Check I/O information of disk')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-d', '--disk', dest='disk', required=True,
                                   type=int, help='Number of the disk to check')

        self.__parser.add_argument('-w', '--warning', dest='warning', required=False,
                                   type=str, help='Warning load. Format: LOAD1,LOAD5,LOAD15')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=False,
                                   type=str, help='Critical load. Format: LOAD1,LOAD5,LOAD15')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__disk_id = args.disk

        warning = args.warning
        if None is not warning:
            warning = warning.split(',')
            if len(warning) != 3:
                self.__status_builder.unknown(
                    Output('Format for warning load mismatch. Expected Format: LOAD1,LOAD5,LOAD15'))
                self.__status_builder.exit()
            self.__warning = [int(warning[0]), int(warning[1]), int(warning[2])]

        critical = args.critical
        if None is not critical:
            critical = critical.split(',')
            if len(critical) != 3:
                self.__status_builder.unknown(
                    Output('Format for critical load mismatch. Expected Format: LOAD1,LOAD5,LOAD15'))
                self.__status_builder.exit()
            self.__critical = [int(critical[0]), int(critical[1]), int(critical[2])]

        if None is self.__warning and self.__critical is not None:
            self.__status_builder.unknown(Output('If critical load is defined, you have to set warning load'))
            self.__status_builder.exit()

        if None is not self.__warning and self.__critical is None:
            self.__status_builder.unknown(Output('If warning load is defined, you have to set critical load'))
            self.__status_builder.exit()

    def run(self):
        oids = self.__snmp_executor.run()

        status_data = {}

        keys = {
            '2': 'device',
            '3': 'bytesRead32',
            '4': 'bytesWrite32',
            '5': 'reads',
            '6': 'writes',
            '8': 'load',
            '9': 'load1',
            '10': 'load5',
            '11': 'load15',
            '12': 'bytesRead64',
            '13': 'bytesWrite64',
            '14': 'serialNumber',
        }
        for oid in oids:
            base = oid['oid'].split('.')

            id = int(base[1])

            if base[0] == '1' or int(base[1]) != self.__disk_id:
                continue

            data = status_data.get(id, {})
            data[keys.get(base[0])] = oid['value']
            status_data[id] = data

        if 0 == len(status_data):
            self.__status_builder.unknown(Output(f'Disk "{self.__disk_id}" either does not exist or not accessible'))
            self.__status_builder.exit()

        for status_data_id in status_data:
            data = status_data[status_data_id]

            perfdata = [
                Perfdata("load15", data['load15']),
                Perfdata("bytesRead32", data['bytesRead32']),
                Perfdata("bytesRead64", data['bytesRead64']),
                Perfdata("bytesWrite32", data['bytesWrite32']),
                Perfdata("bytesWrite64", data['bytesWrite64']),
                Perfdata("reads", data['reads']),
                Perfdata("writes", data['writes']),
            ]
            if None is self.__warning:
                perfdata += [
                    Perfdata("load", data['load']),
                    Perfdata("load1", data['load1']),
                    Perfdata("load5", data['load5']),
                ]
            else:
                perfdata += [
                    Perfdata("load", data['load'], warning=self.__warning[0], critical=self.__critical[0]),
                    Perfdata("load1", data['load1'], warning=self.__warning[0], critical=self.__critical[0]),
                    Perfdata("load5", data['load5'], warning=self.__warning[0], critical=self.__critical[0]),
                ]

            output = Output(f"Disk \"{data['device']}\" [{data.get('serialNumber', 'unknown serial number')}]",
                            perfdata)

            if None is self.__warning:
                self.__status_builder.success(output)
            else:
                if self.__critical[0] <= data['load1'] \
                        or self.__critical[1] <= data['load5'] \
                        or self.__critical[2] <= data['load15']:
                    self.__status_builder.critical(output)
                elif self.__warning[0] <= data['load1'] \
                        or self.__warning[1] <= data['load5'] \
                        or self.__warning[2] <= data['load15']:
                    self.__status_builder.warning(output)
                else:
                    self.__status_builder.success(output)
