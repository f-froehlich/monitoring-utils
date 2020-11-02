#!/usr/bin/python3
# -*- coding: utf-8

#  Monitoring monitoring-utils
#
#  Monitoring monitoring-utils are the background magic for my plugins, scripts and more
#
#  Copyright (c) 2020 Fabian Fröhlich <mail@confgen.org> https://icinga2.confgen.org
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


import subprocess
import sys


class GroupMembers:

    def __init__(self, group, users):
        self.__users = users
        self.__group = group
        self.__current_members = self.get_current_members()

    def main(self):

        not_existing_users = []
        exist_on_server_but_shouldnt = []

        for current in self.__current_members:
            if current not in self.__users:
                exist_on_server_but_shouldnt.append(current)

        for expected in self.__users:
            if expected not in self.__current_members:
                not_existing_users.append(expected)

        if 0 != len(exist_on_server_but_shouldnt):
            print(
                "CRITICAL: There are some users in group '" + self.__group + "', which are not expected! Not expected users: " + ", ".join(
                    exist_on_server_but_shouldnt))
            sys.exit(2)

        if 0 != len(not_existing_users):
            print(
                "WARNING: There are some users not in group '" + self.__group + "', which are expected! Expected additional users: " + ", ".join(
                    not_existing_users))
            sys.exit(1)

        print("OK")
        sys.exit(0)

    def get_current_members(self):
        out = subprocess.Popen(['getent', 'group', self.__group],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = out.communicate()

        if 0 != out.returncode:
            stderr = stderr.decode("utf-8")
            print('UNKNOWN: ' + stderr)
            sys.exit(3)

        stdout = stdout.decode("utf-8")

        parsed_config = []
        for config in stdout.split("\n"):
            config = config.split(":")

            if 4 == len(config):
                parsed_config += config[3].split(",")

        return parsed_config
