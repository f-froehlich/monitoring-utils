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


class NmapScriptExecutor:

    def __init__(self, logger, status_builder):
        self.__logger = logger
        self.__status_builder = status_builder
        self.__scripts = {}

    def add_script(self, script_name, script):
        self.__scripts[script_name] = script

    def execute(self, open_ports, ignore_port):
        self.__logger.info('Checking reports')

        executed_scripts = {}
        not_executed_scripts = {}

        for port_report in open_ports:
            self.__logger.debug('Check ciphers port report "' + str(port_report) + '"')
            port = port_report['portid']

            if port in ignore_port:
                self.__logger.info('Found port config for port "' + port + '" but it is also in excluded ports.')
                self.__logger.debug('Ignoring port "' + port + '"')
                continue

            self.__logger.info('Checking configuration of port "' + port + '"')

            scripts = port_report.get('scripts', None)
            if None == scripts:
                self.__logger.debug('No Script seams not to be executed, can\'t proceed')
                self.__status_builder.unknown('No script seams not to be executed, can\'t proceed')
                self.__status_builder.exit()

            executed = executed_scripts.get(port, [])
            for script in scripts:
                script_runner = self.__scripts.get(script['name'], None)

                if script_runner == None:
                    self.__logger.debug('Script "' + script['name'] + '" was executed but no script runner is set.')
                    continue

                expected_report = script_runner.get_parsed_config(port)
                if None == expected_report:
                    self.__logger.info('Port "' + port + '" is open but no configuration is set. Exclude it '
                                                         'with --ignore-port or setup a configuration')
                    self.__status_builder.warning('Port "' + port + '" is open but no configuration is set. Exclude it '
                                                                    'with --ignore-port or setup a configuration')
                    self.__logger.debug('Ignoring port "' + port + '"')
                    continue

                self.__logger.info('Execute script "' + script['name'] + '".')
                script_runner.run(script, expected_report, port)
                executed.append(script['name'])
                self.__logger.info('Script "' + script['name'] + '" executed.')

            not_executed = not_executed_scripts.get(port, [])
            for script in self.__scripts:
                if script not in executed_scripts:
                    not_executed.append(script)
                    self.__logger.info('Script "' + script + '" was not executed because it was not found in '
                                                             'scan report.')

            executed_scripts[port] = executed
            not_executed_scripts[port] = not_executed

        return executed_scripts, not_executed_scripts
