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


class GPUInfo(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__gpu_id = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.6574.108'

        Plugin.__init__(self, 'Check GPU information')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-g', '--gpu', dest='gpu', required=True,
                                   type=int, help='Number of the gpu to check')

        self.__parser.add_argument('-w', '--warning', dest='warning', required=False,
                                   type=int, help='Warning usage (%)')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=False,
                                   type=int, help='Critical usage (%)')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__gpu_id = args.gpu
        self.__warning = args.warning
        self.__critical = args.critical

        failed = False
        if None is not self.__critical:
            if self.__critical > 100:
                self.__status_builder.unknown(Output('Critical value can\'t be greater than 100 %'))
                failed = True
            elif self.__critical < 0:
                self.__status_builder.unknown(Output('Critical value must be at least 0 %'))
                failed = True

        if None is not self.__warning:

            if self.__warning < 0:
                self.__status_builder.unknown(Output('Warning value must be at least 0 %'))
                failed = True

        if None is not self.__critical and None is self.__warning:
            self.__status_builder.unknown(Output('If you set a critical bound you have to specify a warning bound'))
            failed = True
        elif None is self.__critical and None is not self.__warning:
            self.__status_builder.unknown(Output('If you set a warning bound you have to specify a critical bound'))
            failed = True
        elif None is not self.__critical and None is not self.__warning:
            if self.__warning > self.__critical:
                self.__status_builder.unknown(Output('Warning value can\'t be greater than critical value'))
                failed = True

        if failed:
            self.__status_builder.exit()

    def run(self):
        oids = self.__snmp_executor.run()

        status_data = {}

        keys = {
            '1': 'supported',
            '2': 'utilization',
            '3': 'usage',
            '4': 'free',
            '5': 'used',
            '6': 'total',
        }
        for oid in oids:
            base = oid['oid'].split('.')
            id = int(base[1])

            if int(base[1]) != self.__gpu_id:
                continue

            data = status_data.get(id, {})
            data[keys.get(base[0])] = oid['value']
            status_data[id] = data

        if 0 == len(status_data):
            self.__status_builder.unknown(Output(f'GPU "{self.__gpu_id}" either does not exist or not accessible'))
            self.__status_builder.exit()

        for status_data_id in status_data:
            data = status_data[status_data_id]

            if 1 == data['supported']:
                output = Output(f"GPU \"{self.__gpu_id}\" is unsupported")
                self.__status_builder.unknown(output)
                continue

            if None is self.__warning:
                perfdata = [
                    Perfdata(f'{self.__gpu_id}', data['used'], min=0, max=data['total']),
                ]
            else:
                perfdata = [
                    Perfdata(f'{self.__gpu_id}', data['used'], warning=self.__warning / 100 * data['total'],
                             critical=self.__critical / 100 * data['total'], min=0, max=data['total']),
                ]

            output = Output(f"GPU \"{self.__gpu_id}\"", perfdata)

            if None is self.__warning:
                self.__status_builder.success(output)
            else:
                if self.__critical <= data['usage']:
                    self.__status_builder.critical(output)
                elif self.__warning <= data['usage']:
                    self.__status_builder.warning(output)
                else:
                    self.__status_builder.success(output)
