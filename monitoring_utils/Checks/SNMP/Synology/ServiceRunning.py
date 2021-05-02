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


class ServiceRunning(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__services = None
        self.__oid = '1.3.6.1.4.1.6574.6.1.1'

        Plugin.__init__(self, 'Check if the services running')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-s', '--service', dest='services', action='append', default=[],
                                   type=str, help='Service, which should run. Can be repeated')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__services = args.services

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

        for service in self.__services:
            found = False
            for services_running_id in services_running:
                config = services_running[services_running_id]
                if config['service'] == service:
                    found = True
                    self.__status_builder.success(
                        Output(f'Service "{service}" up and running', [Perfdata(f'{service}', config["users"])]))
                    break

            if not found:
                self.__status_builder.critical(Output(f'Service "{service}" should running but it doesn\'t'))

        for services_running_id in services_running:
            config = services_running[services_running_id]
            found = False
            for service in self.__services:
                if service == config['service']:
                    found = True
                    break

            if not found:
                self.__status_builder.warning(Output(f'Service "{config["service"]}" is running but it shouldn\'t',
                                                     [Perfdata(f'{config["service"]}', config["users"])]))

        self.__status_builder.exit(True)
