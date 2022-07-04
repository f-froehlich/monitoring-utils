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
from monitoring_utils.Core.Executor.ApchectlExecutor import ApachectlExecutor
from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Plugin.Plugin import Plugin


class ProxyRequests(Plugin):

    def __init__(self):

        self.__critical_content = None
        self.__warning_content = None
        self.__allow = None
        self.__apachectl_executor = None
        Plugin.__init__(self, 'Check if ProxyRequests (open proxy) is disabled or enabled')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__parser.add_argument('-a', '--allow', dest='allow', action='append', default=[],
                                   help='Files to allow ProxyRequests')

    def configure(self, args):
        self.__allow = args.allow
        self.__apachectl_executor = ApachectlExecutor(self.__logger, self.__status_builder)

    def run(self):
        running_config = self.__apachectl_executor.get_running_config()

        proxy_exists = False
        for file in running_config:
            config = running_config[file]
            is_enabled = False
            for c in config:
                option = c['option'].lower()
                if "proxyrequests" in option and "on" in option:
                    is_enabled = True
                    proxy_exists = True
                    if file in self.__allow:
                        self.__status_builder.success(
                            Output(
                                f'Open proxy detected and it is allowed. File: "{file}", line: "{c["line"]}"'
                            )
                        )
                    else:
                        self.__status_builder.critical(
                            Output(
                                f'Open proxy detected! File: "{file}", line: "{c["line"]}"'
                            )
                        )
            if file in self.__allow and not is_enabled:
                self.__status_builder.warning(
                    Output(
                        f'Open proxy not configured but it should be in file: "{file}"'
                    )
                )
        for allowed_file in self.__allow:
            if None is running_config.get(allowed_file, None):
                self.__status_builder.warning(
                    Output(
                        f'Open proxy not configured but it should be in file: "{allowed_file}"'
                    )
                )

        if not proxy_exists:
            self.__status_builder.success(Output(f'No open proxy configured'))
