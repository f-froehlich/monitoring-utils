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


import subprocess


class CLIExecutor:

    def __init__(self, logger, status_builder, command_array, ignore_empty_lines=True):
        self.__command_array = command_array
        self.__ignore_empty_lines = ignore_empty_lines
        self.__status_builder = status_builder
        self.__logger = logger

    def run(self):

        command = ', '.join(self.__command_array)
        self.__logger.debug('Run command "' + command + '" on host.')

        out = subprocess.Popen(self.__command_array,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = out.communicate()
        self.__logger.debug('Command exit with exit code: ' + str(out.returncode))

        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        self.__logger.debug('stdout: "' + stdout + '"')
        self.__logger.debug('stderr: "' + stderr + '"')
        if 0 != out.returncode:
            if 'a password is required' in stderr:
                self.__logger.debug('Can\'t run sudo without password')

                self.__status_builder.unknown(
                    'Can\'t run sudo without password. Please give executable rights without password in /ets/sudoers for sshd command. See our documentation for details.')
            else:
                self.__status_builder.unknown(stderr)

            self.__status_builder.exit()

        if not self.__ignore_empty_lines:
            return stdout.split("\n")

        self.__logger.info('Filter empty lines')
        lines = []
        for line in stdout.split("\n"):
            if line != '':
                lines.append(line)

        return lines
