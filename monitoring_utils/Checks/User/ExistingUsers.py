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


class ExistingUsers(Plugin):

    def __init__(self):
        self.__users = None
        self.__uid_min = None
        self.__uid_max = None
        self.__shell_filter = None
        self.__current_members = None

        Plugin.__init__(self, 'Check the group members on the host')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-m', '--uid-min', dest='minuid', default=-1, type=int, help='Minimum userid')
        self.__parser.add_argument('-M', '--uid-max', dest='maxuid', default=-1, type=int, help='Maximum userid')
        self.__parser.add_argument('-u', '--user', dest='users', action='append', default=[],
                                   help='Normal not sudoer user. USERNAME')
        self.__parser.add_argument('-S', '--filter-shell', dest='shellfilter', action='append', default=[],
                                   help='Excluded list of shells')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__uid_min = args.minuid
        self.__uid_max = args.maxuid
        self.__users = args.users
        self.__shell_filter = args.shellfilter
        self.__current_members = self.get_current_members()

    def run(self):
        current_usernames = []
        self.__logger.info('Check user from host')
        for current in self.__current_members:
            self.__logger.debug('Check user "' + current['username'] + '"')
            current_usernames.append(current['username'])
            if current['username'] not in self.__users:
                self.__logger.info('User "' + current['username'] + '" exist on host but shouldn\'t')
                self.__status_builder.critical('User "' + current['username'] + '" exist on host but shouldn\'t')

        self.__logger.info('Check user, who should exist')
        for user in self.__users:
            if user not in current_usernames:
                self.__logger.debug('Check user "' + user + '"')
                self.__status_builder.warning('User "' + user + '" should exist on host but don\'t')

        self.__status_builder.success('All checks passed.')

    def get_current_members(self):
        self.__logger.info('Parsing /etc/passwd')
        cli_executor = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                   command_array=['cat', '/etc/passwd'])
        output = cli_executor.run()

        parsed_users = []
        for line in output:
            config = line.split(":")

            if 7 != len(config):
                continue

            self.__logger.debug('Parsing line "' + line + '"')
            if -1 < self.__uid_min and int(config[2]) < self.__uid_min:
                self.__logger.debug('Skipping because uid of user is too low')
                continue

            if -1 < self.__uid_max < int(config[2]):
                self.__logger.debug('Skipping because uid of user is too high')
                continue

            if config[6] in self.__shell_filter:
                self.__logger.debug('Skipping because shell of user should be filtered')
                continue

            self.__logger.debug('User "' + config[0] + '" marked for checking')

            parsed_users.append({
                "username": config[0],
                "uid": int(config[2]),
                "gid": int(config[3]),
                "home": config[5],
                "shell": config[6],
            })

        return parsed_users
