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


class SMART(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__disk_id = None
        self.__oid = '1.3.6.1.4.1.6574.5.1.1'

        Plugin.__init__(self, 'Check the SMART status of a specific disk')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-d', '--disk', dest='disk', required=True,
                                   type=int, help='Number of the disk to check')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__disk_id = args.disk

    def run(self):
        oids = self.__snmp_executor.run()

        first_datapoint = self.__disk_id * 17 - 16
        last_datapoint = self.__disk_id * 17

        status_data = {}

        keys = {
            '3': 'attributeName',
            '4': 'attributeId',
            '5': 'current',
            '6': 'worst',
            '7': 'threshold',
            '8': 'raw',
            '9': 'status',
        }
        for oid in oids:
            base = oid['oid'].split('.')

            id = int(base[1])

            if base[0] in ['1', '2'] or id < first_datapoint or id > last_datapoint:
                continue

            data = status_data.get(id, {})
            data[keys.get(base[0])] = oid['value']
            status_data[id] = data

        critical_values = ['pre-fail', 'pre fail', 'pre_fail', 'old-age', 'old age', 'old_age']
        for status_data_id in status_data:
            data = status_data[status_data_id]

            perfdata = [
                Perfdata(f"{data['attributeName']}.id", data['attributeId']),
                Perfdata(f"{data['attributeName']}.status", data['status']),
                Perfdata(f"{data['attributeName']}.current", data['current']),
                Perfdata(f"{data['attributeName']}.threshold", data['threshold']),
                Perfdata(f"{data['attributeName']}.worst", data['worst']),
                Perfdata(f"{data['attributeName']}.raw", data['raw']),
            ]

            output = Output(f"{data['attributeName']} [{data['attributeId']}] is \"{data['status']}\" current: " \
                            f"{data['current']}, worst: {data['worst']}, threshold: {data['threshold']}, raw: " \
                            f"{data['raw']}", perfdata)

            if data['status'].lower() == 'ok':
                self.__status_builder.success(output)
            elif data['status'].lower() in critical_values:
                self.__status_builder.critical(output)
            else:
                self.__status_builder.warning(output)
