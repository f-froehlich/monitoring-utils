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


class DiskTemperature(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__num_disks = None
        self.__warning = None
        self.__critical = None
        self.__spare = None
        self.__oid = '1.3.6.1.4.1.6574.2.1.1'

        Plugin.__init__(self, 'Check The temperature of the disks')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-d', '--disks', dest='disks', required=True,
                                   type=int, help='Number of disks')

        self.__parser.add_argument('-w', '--warning', dest='warning', required=True,
                                   type=int, help='Warning temperature')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=True,
                                   type=int, help='Critical temperature')
        self.__parser.add_argument('--spare', dest='spare', type=int, required=False, action='append', default=[],
                                   help='Id(s) of Hot-Spare Disk(s) (can be repeated)')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__num_disks = args.disks
        self.__warning = args.warning
        self.__critical = args.critical
        self.__spare = args.spare

    def run(self):
        oids = self.__snmp_executor.run()

        disk_oid_factor = 0 # default < DSM 7.0
        for oid in oids:
            disk_oid_factor = max(disk_oid_factor, int(oid['oid'].split('.')[0]))

        if len(oids) != self.__num_disks * disk_oid_factor:
            self.__status_builder.unknown(Output(
                'You try to check "{disks}" but there are "{configured}" disks in your system.'.format(
                    disks=self.__num_disks, configured=int(len(oids) / disk_oid_factor))))
            self.__status_builder.exit()

        disks = [{} for i in range(0, self.__num_disks)]

        for oid in oids:
            base = oid['oid'].split('.')
            disk_id = int(base[1])

            if '1' == base[0]:
                disks[disk_id]['index'] = oid['value']
            elif '2' == base[0]:
                disks[disk_id]['id'] = oid['value']
            elif '3' == base[0]:
                disks[disk_id]['model'] = oid['value']
            elif '4' == base[0]:
                disks[disk_id]['type'] = oid['value']
            elif '5' == base[0]:
                if disk_id + 1 in self.__spare:
                    disks[disk_id]['status'] = 0
                else:
                    disks[disk_id]['status'] = oid['value']
            elif '6' == base[0]:
                disks[disk_id]['temperature'] = oid['value']

            if disk_oid_factor >= 6:
                if '7' == base[0]:
                    disks[disk_id]['diskRole'] = oid['value']
                elif '8' == base[0]:
                    disks[disk_id]['diskRetry'] = oid['value']
                elif '9' == base[0]:
                    disks[disk_id]['diskBadSector'] = oid['value']
                elif '10' == base[0]:
                    disks[disk_id]['diskIdentifyFail'] = oid['value']
                elif '11' == base[0]:
                    disks[disk_id]['diskRemainLife'] = oid['value']
                elif '12' == base[0]:
                    disks[disk_id]['diskRemainLife'] = oid['value']

            if disk_oid_factor >= 13:
                if '13' == base[0]:
                    disks[disk_id]['diskHealthStatus'] = oid['value']


        for disk in disks:
            if self.__critical <= disk['temperature']:
                self.__status_builder.critical(
                    Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))
            elif self.__warning <= disk['temperature']:
                if 4 <= disk['status']:
                    self.__status_builder.critical(
                        Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))
                else:
                    self.__status_builder.warning(
                        Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))
            else:
                if 4 <= disk['status']:
                    self.__status_builder.critical(
                        Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))
                elif 2 <= disk['status']:
                    self.__status_builder.warning(
                        Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))
                else:
                    self.__status_builder.success(
                        Output(self.__get_disk_description(disk), self.__get_disk_perfdata(disk)))

        self.__status_builder.exit(True)

    def __get_disk_description(self, disk):

        status = {
            0: 'Not initialized (Hot Spare)',
            1: 'Normal',
            2: 'No data',
            3: 'Not initialized',
            4: 'System partition failed',
            5: 'Crashed',
        }

        return disk['id'] + ' - ' + status[disk['status']] + ' / temperature "' + str(disk['temperature']) \
               + '°C" (' + str(disk['model']) + ' - ' + str(disk['type']) + ')'

    def __get_disk_perfdata(self, disk):
        return [
            Perfdata(disk['id'], disk['temperature'], unit='°C', warning=self.__warning, critical=self.__critical),
        ]
