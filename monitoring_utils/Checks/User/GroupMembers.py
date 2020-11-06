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


from monitoring_utils.Core.Executor.CLIExecutor import CLIExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class GroupMembers(Plugin):

    def __init__(self):
        self.__users = None
        self.__group = None
        Plugin.__init__(self, 'Check the members of a group')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-g', '--group', dest='group', default='sudo', help='Group to check the members')
        self.__parser.add_argument('-u', '--user', dest='users', action='append', default=[],
                                   help='User, who should be in group')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__users = args.users
        self.__group = args.group

        self.__current_members = self.get_current_members()

    def run(self):

        self.__logger.info('Checking current existing group members')
        for current in self.__current_members:
            if current not in self.__users:
                self.__logger.info('User "' + current + '" should not be a member of group "' + self.__group + '"')
                self.__status_builder.critical('User "' + current + '" should not be a member of group "' +
                                               self.__group + '"')

        self.__logger.info('Checking expected group members')
        for expected in self.__users:
            if expected not in self.__current_members:
                self.__logger.info('User "' + expected + '" should be a member of group "' + self.__group + '"')
                self.__status_builder.warning('User "' + expected + '" should be a member of group "' + self.__group
                                              + '"')

        self.__status_builder.success('All checks passed.')

    def get_current_members(self):
        self.__logger.info('Check if group "' + self.__group + '" exist')
        cli_executor_group_exist = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                               command_array=['cat', '/etc/group'])
        group_output = cli_executor_group_exist.run()
        group_exists = False
        for line in group_output:
            self.__logger.debug('Check line "' + line + '" of /etc/group')
            if self.__group == line.split(':')[0]:
                self.__logger.debug('Group exist.')
                group_exists = True
                break
        if not group_exists:
            self.__status_builder.unknown('Group "' + self.__group + '" does not exist on host')
            self.__status_builder.exit()

        self.__logger.info('Parsing members of "' + self.__group + '"')
        cli_executor_group_members = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                                 command_array=['getent', 'group', self.__group])
        output = cli_executor_group_members.run()
        parsed_config = []
        for line in output:
            self.__logger.debug('Check line "' + line + '" of /etc/group')
            config = line.split(":")

            if 4 == len(config):
                self.__logger.debug('User "' + config[3].split(",")[0] + '" is in group "' + self.__group + '"')
                parsed_config += config[3].split(",")
            else:
                self.__logger.debug('Could not parse line')

        return parsed_config
