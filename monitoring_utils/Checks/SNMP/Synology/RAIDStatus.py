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


class RAIDStatus(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__num_raids = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.6574.3.1.1'

        Plugin.__init__(self, 'Check The RAID status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-r', '--raids', dest='disks', required=True,
                                   type=int, help='Number of RAIDs')

        self.__parser.add_argument('-w', '--warning', dest='warning', required=True,
                                   type=int, help='Warning free disk space (%)')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=True,
                                   type=int, help='Critical disk space (%)')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__num_raids = args.disks
        self.__warning = args.warning
        self.__critical = args.critical

        failed = False
        if self.__critical > 100:
            self.__status_builder.unknown(Output('Critical value can\'t be greater than 100 %'))
            failed = True
        elif self.__critical < 0:
            self.__status_builder.unknown(Output('Critical value must be at least 0 %'))
            failed = True

        if self.__warning > self.__critical:
            self.__status_builder.unknown(Output('Warning value can\'t be greater than critical value'))
            failed = True

        elif self.__warning < 0:
            self.__status_builder.unknown(Output('Warning value must be at least 0 %'))
            failed = True

        if failed:
            self.__status_builder.exit()

    def run(self):
        oids = self.__snmp_executor.run()

        if len(oids) != self.__num_raids * 5:
            self.__status_builder.unknown(Output(
                'You try to check "{disks}" RAIDs but there are "{configured}" RAIDs in your system.'.format(
                    disks=self.__num_raids, configured=int(len(oids) / 5))))
            self.__status_builder.exit()

        raids = [{} for i in range(0, self.__num_raids)]

        for oid in oids:
            base = oid['oid'].split('.')
            disk_id = int(base[1])

            if '1' == base[0]:
                raids[disk_id]['index'] = oid['value']
            elif '2' == base[0]:
                raids[disk_id]['name'] = oid['value']
            elif '3' == base[0]:
                raids[disk_id]['status'] = oid['value']
            elif '4' == base[0]:
                raids[disk_id]['free'] = oid['value']
            elif '5' == base[0]:
                raids[disk_id]['total'] = oid['value']

        status = {
            1: 'Normal',
            2: 'Repairing',
            3: 'Migrating',
            4: 'Expanding',
            5: 'Deleting',
            6: 'Creating',
            7: 'Raid syncing',
            8: 'Raid parity checking',
            9: 'Raid assembling',
            10: 'Canceling',
            11: 'Degrade',
            12: 'Crashed',
            13: 'Data scrubbing',
            14: 'Raid deploying',
            15: 'Raid undeploying',
            16: 'Raid mount cache',
            17: 'Raid unmount cache',
            18: 'Raid expanding unfinised SHR',
            19: 'Raid convert SHR to pool',
            20: 'Raid migrate SHR1 to HR2',
            21: 'Raid unknown status',
        }

        warning_states = [2, 3, 4, 13, 15]
        unknown_states = [6, 7, 8, 9, 14, 16, 17, 18, 19, 20, 21]
        critical_states = [5, 10, 11, 12]

        for raid in raids:
            usage = raid['total'] - raid['free']
            usage_percent = usage / raid['total'] * 100

            perfdata = [
                Perfdata(f'{raid["name"]}', usage, warning=self.__warning / 100 * raid['total'],
                         critical=self.__critical / 100 * raid['total'], min=0, max=raid['total']),
            ]

            output = Output(raid['name'] + ' - ' + status[raid['status']] + ' (' + str(usage_percent) + ' % used - '
                            + str(usage) + ' / ' + str(raid['total']) + ')', perfdata)

            if self.__critical <= usage_percent:
                self.__status_builder.critical(output)
            elif self.__warning <= usage_percent:
                if raid['status'] in critical_states:
                    self.__status_builder.critical(output)
                else:
                    self.__status_builder.warning(output)
            else:
                if raid['status'] in critical_states:
                    self.__status_builder.critical(output)
                elif raid['status'] in warning_states:
                    self.__status_builder.warning(output)
                elif raid['status'] in unknown_states:
                    self.__status_builder.unknown(output)
                else:
                    self.__status_builder.success(output)

        self.__status_builder.exit(True)
