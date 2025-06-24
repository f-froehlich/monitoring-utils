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
import json
from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Plugin.Plugin import Plugin
from monitoring_utils.Core.Executor.CLIExecutor import CLIExecutor


class SystemdServiceNoFailed(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__except = []

        Plugin.__init__(self, 'Check if a systemd service is failed')

    def add_args(self):
        self.__parser = self.get_parser()

        self.__parser.add_argument( '--except', dest='exceptunit', action='append',
                                   help='Except a unit. List only units witch are allowed to be in failed state', default=[])


    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__except = args.exceptunit

    def run(self):
        cli_executor = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                   command_array=['systemctl', 'list-units', '--state=failed', '--output=json'])
        output = cli_executor.run()
        print(output)

        if 1 != len(output):
            self.__status_builder.unknown(f'No valid output {output}')
            self.__status_builder.exit()

        data = json.loads(output[0])

        if 0 == len(data):
            self.__status_builder.success(f'No failed unit found')
            self.__status_builder.exit()

        has_error = False
        for unit in data:
            if unit['unit'] in self.__except:
                self.__logger.info(f'Unit {unit["unit"]} has state {unit['active']} ({unit['load']}; sub: {unit["sub"]}) - {unit["description"]} but is excluded')
                continue
            else:
                has_error = True
                self.__status_builder.critical(f'Unit {unit["unit"]} has state {unit['active']} ({unit['load']}; sub: {unit["sub"]}) - {unit["description"]}')

        if not has_error:
            self.__status_builder.success(f'No failed unit found')


