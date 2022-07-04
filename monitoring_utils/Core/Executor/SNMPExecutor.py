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


class SNMPExecutor:

    def __init__(self, logger, status_builder, parser, oid, username=None, password=None, host=None, snmp_version=None,
                 community=None):
        self.__oid = oid
        self.__host = host
        self.__snmp_version = snmp_version
        self.__username = username
        self.__password = password
        self.__community = community
        self.__status_builder = status_builder
        self.__parser = parser
        self.__logger = logger
        self.__cli_executor = None

    def configure(self, args):
        self.__username = args.username
        self.__password = args.password
        self.__host = args.host
        self.__community = args.community
        self.__snmp_version = args.version

        if '3' == self.__snmp_version:
            if None is self.__username:
                self.__status_builder.unknown('Require a username')
                self.__status_builder.exit()
            if None is self.__password:
                self.__status_builder.unknown('Require a password')
                self.__status_builder.exit()

        cliargs = [
            'snmpwalk', '-v', self.__snmp_version, '-t', str(args.timeout), '-l', 'authNoPriv', self.__host, self.__oid,
            '-O', 'n'
        ]
        if None is not self.__username:
            cliargs += ['-u', self.__username, ]

        if None is not self.__password:
            cliargs += ['-A', self.__password, ]

        if None is not self.__community:
            cliargs += ['-c', self.__community, ]

        self.__cli_executor = CLIExecutor(self.__logger, self.__status_builder, cliargs)

    def add_args(self):
        self.__parser.add_argument('-u', '--username', dest='username', type=str, help='Username')
        self.__parser.add_argument('-p', '--password', dest='password', type=str, help='Password')
        self.__parser.add_argument('-H', '--host', dest='host', required=True, type=str, help='Host')
        self.__parser.add_argument('--version', dest='version', required=True, type=str, help='SNMP Version to use',
                                   choices=['1', '2c', '3'], default='3')
        self.__parser.add_argument('--community', dest='community', type=str, help='SNMP community to use')

    def run(self):
        self.__logger.debug('Request SNMP OID "' + self.__oid + '" on host "' + self.__host + '".')
        output = self.__cli_executor.run()
        error = False
        configs = []
        for line in output:
            if 'No Such Object available' in line:
                self.__status_builder.unknown(line)
                error = True
                continue

            if '= ""' in line:
                continue
            splittet = line.split(' = ')
            splittet_type = splittet[1].split(':')
            if 2 > len(splittet_type):
                self.__status_builder.unknown(f'Could not parse line "{line}"')
                error = True
                continue

            type = splittet_type[0].strip().lower()
            value = ':'.join(splittet_type[1:]).replace('"', '').strip()

            if 'integer' == type:
                value = int(value)
            elif 'counter32' == type:
                value = int(value)
            elif 'counter64' == type:
                value = int(value)
            elif 'gauge32' == type:
                value = int(value)
            elif 'hex-string' == type:
                value = str(value)
            elif 'ipaddress' == type:
                value = str(value)
            elif 'oid' == type:
                value = str(value)
            elif 'string' == type:
                if isinstance(value, float):
                    value = float(value)
                elif isinstance(value, int):
                    value = int(value)
                else:
                    value = str(value)
            elif 'opaque' == type:
                value = str(value)
            elif 'timeticks' == type:
                value = str(value)
            else:
                self.__logger.debug(f'Got unknown type {type} -> ignoring')
                continue

            configs.append({
                'oid': splittet[0].replace('.' + self.__oid + '.', '').replace('.' + self.__oid, ''),
                'value': value,
                'type': type
            })

        if error:
            self.__status_builder.exit()

        return configs
