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


class SSHDSecurity:

    def __init__(self, permitrootlogin='no', pubkeyauthentication='yes', passwordauthentication='no',
                 permitemptypasswords='no', fingerprinthash='SHA256', port=22, config=[]):

        self.__config = config
        self.__port = port
        self.__fingerprinthash = fingerprinthash
        self.__permitemptypasswords = permitemptypasswords
        self.__passwordauthentication = passwordauthentication
        self.__pubkeyauthentication = pubkeyauthentication
        self.__permitrootlogin = permitrootlogin
        self.__running_config = self.get_running_config()

    def main(self):

        self.check_value('permitrootlogin', [self.__permitrootlogin])
        self.check_value('pubkeyauthentication', [self.__pubkeyauthentication])
        self.check_value('passwordauthentication', [self.__passwordauthentication])
        self.check_value('permitemptypasswords', [self.__permitemptypasswords])
        self.check_value('fingerprinthash', [self.__fingerprinthash])
        self.check_value('port', [self.__port])

        for arg in self.__config:
            print(arg)
            config = config.split("=")
            self.check_value(config[0], config[1].split("|"))

        print("OK")
        sys.exit(0)

    def check_value(self, option, expected_array):

        if 1 == len(expected_array):
            expected = expected_array[0]
            for config in self.__running_config:
                if config[0] == option:
                    if str(config[1]).lower() != str(expected).lower():
                        print(
                            "CRITICAL: Configuration does not match expected value for param " + option + ". Expected: " + str(
                                expected) + " got: " + str(config[1]))
                        sys.exit(2)
                    return
            print("WARNING: Can't find expected configuration " + option + ". Expected: " + str(expected))
            sys.exit(1)
        else:
            current_values = []
            for config in self.__running_config:
                if config[0] == option:
                    current_values.append(config[1])

            not_existing_in_config = []
            exist_in_config_but_not_expected = []

            for expected in expected_array:
                if expected not in current_values:
                    not_existing_in_config.append(expected)

            for current in current_values:
                if current not in expected_array:
                    exist_in_config_but_not_expected.append(current)

            if 0 != len(not_existing_in_config):
                print(
                    "CRITICAL: There are some values of configuration '" + option + "' expected, which are not configured yet! Not configured values: " + ", ".join(
                        not_existing_in_config))
                sys.exit(2)

            if 0 != len(exist_in_config_but_not_expected):
                print(
                    "WARNING: There are some values of configuration '" + option + "' configured, which are not expected! Not expected values: " + ", ".join(
                        exist_in_config_but_not_expected))
                sys.exit(1)

    def get_running_config(self):
        out = subprocess.Popen(['sudo', '-n', 'sshd', '-T'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = out.communicate()

        if 0 != out.returncode:
            stderr = stderr.decode("utf-8")
            if 'a password is required' in stderr:
                print(
                    'UNKNOWN: can\'t run sudo without password. Please give executable rights without password in /ets/sudoers for sshd command.')
            else:
                print('UNKNOWN: ' + stderr)

            sys.exit(3)
        stdout = stdout.decode("utf-8")

        parsed_config = []
        for config in stdout.split("\n"):
            config = config.split(" ")
            key = config[0]
            value = " ".join(config[1:])
            parsed_config.append((key, value))

        return parsed_config
