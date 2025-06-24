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
from datetime import datetime
from pathlib import Path

from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Plugin.Plugin import Plugin
from monitoring_utils.Core.Executor.CLIExecutor import CLIExecutor


class SystemdServiceActive(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__unit_name = None

        Plugin.__init__(self, 'Check if a systemd service is active')

    def add_args(self):
        self.__parser = self.get_parser()

        self.__parser.add_argument('--unit', dest='unit', required=True, type=str,
                                   help='Specify the unit name')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__unit_name = args.unit

    def run(self):

        cli_executor = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                   command_array=['systemctl', 'is-active', self.__unit_name])
        output = cli_executor.run(exit_on_failure=False, no_failure_message=True)
        if 0 == len(output):
            self.__status_builder.unknown(f'No status found for {self.__unit_name}.')
            self.__status_builder.exit()

        if 'not-found' == output[0].lower():
            self.__status_builder.unknown(f'The unit {self.__unit_name} was not found.')
        elif 'active' != output[0].lower():
            self.__status_builder.critical(f'The unit {self.__unit_name} is not active.')
        else:
            self.__status_builder.success(f'The unit {self.__unit_name} is active.')


