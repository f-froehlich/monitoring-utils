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
from typing import List, Dict

from monitoring_utils.Core.Executor.CLIExecutor import CLIExecutor
from monitoring_utils.Core.Outputs.Output import Output


class Apache2ctlExecutor:

    def __init__(self, logger, status_builder):

        self.__status_builder = status_builder
        self.__logger = logger

    def list_enabled_mods(self) -> List[Dict[str, str]]:
        self.__logger.info('List enabled modules')

        unparsed_modules = CLIExecutor(self.__logger, self.__status_builder, ['sudo', 'apache2ctl', '-M']).run()
        parsed_modules = []
        is_module = False
        for line in unparsed_modules:
            if "Loaded Modules" in line:
                is_module = True
            elif is_module:
                module = line.strip().split(' ')
                parsed_modules.append({
                    "name": module[0],
                    "type": module[1].replace('(', '').replace(')', '')
                })

        return parsed_modules

    def is_module_enabled(self, module: str, enabled_modules: List = None) -> bool:
        self.__logger.info(f'Check if module "{module}" is enabled')
        if None is enabled_modules:
            enabled_modules = self.list_enabled_mods()

        for enabled_module in enabled_modules:
            if enabled_module['name'] == module:
                return True
        return False

    def require_module(self, module: str):
        enabled_modules = self.list_enabled_mods()
        if not self.is_module_enabled(module, enabled_modules) \
                and not self.is_module_enabled(f"{module}_module", enabled_modules):
            module = module.replace("_module", "")
            self.__status_builder.unknown(
                Output(
                    f'Required module "mod_{module}" is not enabled. You need to enable it with '
                    f'"sudo a2enmod {module}" and "systemctl restart apache2".'
                )
            )
            self.__status_builder.exit()

    def get_running_config(self) -> List:
        self.require_module("info")
        unparsed_config = CLIExecutor(self.__logger, self.__status_builder,
                                      ['sudo', 'apache2ctl', '-DDUMP_CONFIG']).run()

        parsed_config = {}
        current_file = None
        current_line = None
        for line in unparsed_config:
            if "In file" in line:
                current_file = line.split(':')[1].strip()
            elif "#" == line.strip()[0]:
                current_line = int(line.replace('#', '').replace(':', '').strip())
            else:
                parsed_config[current_file] = parsed_config.get(current_file, []) + [{
                    "line": current_line,
                    "option": line.strip()
                }]

        return parsed_config
