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


class ServiceUsed(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__service = None
        self.__warning = None
        self.__critical = None
        self.__oid = '1.3.6.1.4.1.6574.6.1.1'

        Plugin.__init__(self, 'Check how many users using a service')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-w', '--warning', dest='warning', required=True,
                                   type=int, help='Warning users bound')
        self.__parser.add_argument('-c', '--critical', dest='critical', required=True,
                                   type=int, help='Critical users bound')
        self.__parser.add_argument('-s', '--service', dest='service', required=True,
                                   type=str, help='Service to check user status')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__service = args.service
        self.__warning = args.warning
        self.__critical = args.critical

    def run(self):
        oids = self.__snmp_executor.run()

        services_running = {}

        for oid in oids:
            base = oid['oid'].split('.')

            id = int(base[1])
            config = services_running.get(id, {})

            if '2' == base[0]:
                config['service'] = oid['value'].lower()
            elif '3' == base[0]:
                config['users'] = oid['value']

            services_running[id] = config

        for service_id in services_running:
            config = services_running[service_id]
            if config['service'] == self.__service.lower():
                output = Output(f"Service \"{config['service']}\" is currently used by {config['users']} users.",
                                [Perfdata(config["service"].replace('/', '_'), config["users"])])
                if config['users'] >= self.__critical:
                    self.__status_builder.critical(output)
                elif config['users'] >= self.__warning:
                    self.__status_builder.warning(output)
                else:
                    self.__status_builder.success(output)
                self.__status_builder.exit()

        self.__status_builder.unknown(Output(f'Service "{self.__service}" not found. Is it running?'))
