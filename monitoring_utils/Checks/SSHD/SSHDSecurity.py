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


class SSHDSecurity(Plugin):

    def __init__(self):

        self.__config = []
        self.__running_config = []
        Plugin.__init__(self, 'Check the security of sshd')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-r', '--permit-root-login', dest='permitrootlogin', type=str,
                                   choices=['yes', 'no', 'without-password', 'forced-commands-only'],
                                   default='no', help='Permit root login')
        self.__parser.add_argument('-k', '--public-key-auth', dest='pubkeyauthentication', choices=['yes', 'no'],
                                   default='yes', type=str, help='Public key authentication')
        self.__parser.add_argument('-P', '--password-auth', dest='passwordauthentication', choices=['yes', 'no'],
                                   default='no', help='Password authentication', type=str, )
        self.__parser.add_argument('--permit-empty-passwords', dest='permitemptypasswords', choices=['yes', 'no'],
                                   default='no', type=str, help='Permit empty passwords')
        self.__parser.add_argument('-H', '--fingerprint-hash', dest='fingerprinthash', default='SHA256',
                                   type=str, help='Fingerprint Hash function')
        self.__parser.add_argument('--ignore-fingerprint-hash', dest='ignorefingerprinthash', action='store_true',
                                   help='ignore Fingerprint Hash function')
        self.__parser.add_argument('-p', '--port', dest='port', type=int, default=22, help='Listen port')
        self.__parser.add_argument('-C', '--config', dest='config', action='append', default=[],
                                   help='Other config values to check. Format: OPTION=VALUE_1|VALUE_2|...|VALUE_N')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__config = args.config
        self.__config.append('permitrootlogin=' + args.permitrootlogin)
        self.__config.append('pubkeyauthentication=' + args.pubkeyauthentication)
        self.__config.append('passwordauthentication=' + args.passwordauthentication)
        self.__config.append('permitemptypasswords=' + args.permitemptypasswords)
        self.__config.append('port=' + str(args.port))

        if False is args.ignorefingerprinthash:
            self.__config.append('fingerprinthash=' + args.fingerprinthash)

        self.__running_config = self.get_running_config()

    def run(self):

        for arg in self.__config:
            self.__logger.info('Check config "' + arg + '"')
            config = arg.split("=")
            self.check_value(config[0].lower(), config[1].lower().split("|"))

        self.__status_builder.success('All checks passed.')

    def check_value(self, option, expected_array):

        if 1 == len(expected_array):
            expected = expected_array[0]
            for config in self.__running_config:
                if config[0] == option:
                    configured_value = str(config[1]).lower()
                    expected_value = str(expected)
                    if configured_value != expected_value:
                        self.__logger.debug(
                            'Check not passed: "' + configured_value + '" is not "' + expected_value + '"')
                        self.__status_builder.critical(
                            'Configuration does not match expected value for param "' + option + '". Expected: "'
                            + expected_value + '" got: "' + configured_value + '"')

                    self.__logger.debug(
                        'Check passed: "' + configured_value + '" is not "' + expected_value + '"')
                    return
            self.__status_builder.warning(
                'Can\'t find expected configuration "' + option + '". Expected: "' + str(expected) + '"')

        else:
            current_values = []
            for config in self.__running_config:
                if config[0] == option:
                    current_values.append(config[1])

            for expected in expected_array:
                if expected not in current_values:
                    self.__logger.debug(
                        'Check not passed: "' + str(expected) + '" is not configured on host.')
                    self.__status_builder.critical('"' + option + '" has no value "' + str(expected) + '" on host.')

            for current in current_values:
                if current not in expected_array:
                    self.__logger.debug('Check not passed: "' + str(current) + '" is not expected.')
                    self.__status_builder.warning('"' + option + '" has the value "'
                                                  + str(current) + '" on host but was not expected.')

    def get_running_config(self):
        cli_executor = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                   command_array=['sudo', '-n', 'sshd', '-T'])

        output = cli_executor.run()

        parsed_config = []
        for config in output:
            self.__logger.debug('Parse line: "' + config + '"')
            config = config.lower().split(" ")
            key = config[0]
            value = " ".join(config[1:])
            parsed_config.append((key, value))

        return parsed_config
