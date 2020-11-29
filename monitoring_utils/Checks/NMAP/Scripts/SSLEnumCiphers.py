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


class SSLEnumCiphers:

    def __init__(self, logger, status_builder):
        self.__logger = logger
        self.__status_builder = status_builder
        self.__parsed_config = {}
        self.__open_ports = []

        self.__ignore_port = []
        self.__report = None

        self.__allowed_tlsv1_0_ciphers = None
        self.__allowed_tlsv1_1_ciphers = None
        self.__allowed_tlsv1_2_ciphers = None
        self.__allowed_tlsv1_3_ciphers = None

        self.__least_tlsv1_0_strength = None
        self.__least_tlsv1_1_strength = None
        self.__least_tlsv1_2_strength = None
        self.__least_tlsv1_3_strength = None

        self.__least_strength = None
        self.__least_strength_overall = None

        self.__ignoreciphername = None
        self.__ignorecipherstrength = None
        self.__ignorestrength = None

    def get_parsed_config(self, port):
        return self.__parsed_config.get(port, None)

    def set_report(self, report):
        self.__report = report

    def set_ignore_port(self, ignore_port):
        self.__ignore_port = ignore_port

    def set_ignore_cipher_name(self, config):
        self.__ignoreciphername = config

    def set_ignore_cipher_strength(self, config):
        self.__ignorecipherstrength = config

    def set_ignore_strength(self, config):
        self.__ignorestrength = config

    def set_least_strength(self, strength):
        self.__least_strength = strength

    def set_least_strength_overall(self, strength):
        self.__least_strength_overall = strength

    def set_allowed_tlsv1_0_ciphers(self, ciphers):
        self.__allowed_tlsv1_0_ciphers = ciphers

    def set_least_tlsv1_0_strength(self, strength):
        self.__least_tlsv1_0_strength = strength

    def set_allowed_tlsv1_1_ciphers(self, ciphers):
        self.__allowed_tlsv1_1_ciphers = ciphers

    def set_least_tlsv1_1_strength(self, strength):
        self.__least_tlsv1_1_strength = strength

    def set_allowed_tlsv1_2_ciphers(self, ciphers):
        self.__allowed_tlsv1_2_ciphers = ciphers

    def set_least_tlsv1_2_strength(self, strength):
        self.__least_tlsv1_2_strength = strength

    def set_allowed_tlsv1_3_ciphers(self, ciphers):
        self.__allowed_tlsv1_3_ciphers = ciphers

    def set_least_tlsv1_3_strength(self, strength):
        self.__least_tlsv1_3_strength = strength

    def parse_config(self):
        self.__logger.info('Parsing TLSv1.0 config')
        parsing_error_tls_1_0 = self.parse_cipher_config(self.__allowed_tlsv1_0_ciphers, 'TLSv1.0')
        parsing_error_strength_1_0 = self.parse_strength_config(self.__least_tlsv1_0_strength, 'TLSv1.0')

        self.__logger.info('Parsing TLSv1.1 config')
        parsing_error_tls_1_1 = self.parse_cipher_config(self.__allowed_tlsv1_1_ciphers, 'TLSv1.1')
        parsing_error_strength_1_1 = self.parse_strength_config(self.__least_tlsv1_1_strength, 'TLSv1.1')

        self.__logger.info('Parsing TLSv1.2 config')
        parsing_error_tls_1_2 = self.parse_cipher_config(self.__allowed_tlsv1_2_ciphers, 'TLSv1.2')
        parsing_error_strength_1_2 = self.parse_strength_config(self.__least_tlsv1_2_strength, 'TLSv1.2')

        self.__logger.info('Parsing TLSv1.3 config')
        parsing_error_tls_1_3 = self.parse_cipher_config(self.__allowed_tlsv1_3_ciphers, 'TLSv1.3')
        parsing_error_strength_1_3 = self.parse_strength_config(self.__least_tlsv1_3_strength, 'TLSv1.3')

        self.__logger.info('Parsing overall config')
        parsing_error_strength = self.parse_strength_config(self.__least_strength, 'all')
        parsing_error_strength_all = self.parse_strength_config(['all:' + self.__least_strength_overall], 'all')

        if parsing_error_tls_1_0 \
                or parsing_error_tls_1_1 \
                or parsing_error_tls_1_2 \
                or parsing_error_tls_1_3 \
                or parsing_error_strength_1_0 \
                or parsing_error_strength_1_1 \
                or parsing_error_strength_1_2 \
                or parsing_error_strength_1_3 \
                or parsing_error_strength \
                or parsing_error_strength_all:
            self.__status_builder.exit()

    def parse_cipher_config(self, config, name):
        parsing_error = False
        for port_config in config:
            self.__logger.debug('Parsing cipher config "' + port_config + '"')
            port_config_array = port_config.split(':')
            if 2 != len(port_config_array):
                self.__logger.info('Invalid config "' + port_config + '" detected. Expected format: '
                                                                      'PORT:NAME[,NAME[,NAME ...]]')
                self.__status_builder.unknown('Invalid config "' + port_config + '" detected. Expected format: '
                                                                                 'PORT:NAME[,NAME[,NAME ...]]')
                parsing_error = True
                continue

            port = port_config_array[0]
            ciphers = port_config_array[1].split(',')

            existing_config = self.__parsed_config.get(port, self.get_default_config())

            for cipher in ciphers:
                if '' != cipher and cipher not in existing_config[name]['ciphers']:
                    self.__logger.debug('Add cipher "' + cipher + '" to "' + name + '" of port "' + port + '"')
                    existing_config[name]['ciphers'].append(cipher)

            self.__parsed_config[port] = existing_config

        return parsing_error

    def get_default_config(self):
        return {
            'TLSv1.0': {'ciphers': [], 'strength': None},
            'TLSv1.1': {'ciphers': [], 'strength': None},
            'TLSv1.2': {'ciphers': [], 'strength': None},
            'TLSv1.3': {'ciphers': [], 'strength': None},
            'all': {'strength': None},
        }

    def map_strength(self, strength):
        self.__logger.debug('Map strength "' + strength + '"')
        all_strength = {
            'A': 1,
            'B': 2,
            'C': 3,
            'D': 4,
            'E': 5,
            'F': 6,
        }

        mapped_strength = all_strength.get(strength.upper(), None)
        if None == mapped_strength:
            self.__logger.debug('Invalid strength detected.')
            self.__status_builder.unknown('Invalid strength "' + strength + '" detected. Must be A-F')
            return False, None

        return True, mapped_strength

    def reverse_map_strength(self, strength):
        self.__logger.debug('Reverse map strength "' + str(strength) + '"')
        all_strength = {
            1: 'A',
            2: 'B',
            3: 'C',
            4: 'D',
            5: 'E',
            6: 'F',
        }

        mapped_strength = all_strength.get(strength, None)
        if None == mapped_strength:
            self.__logger.debug('Invalid strength detected.')
            self.__status_builder.unknown('Invalid strength "' + str(strength) + '" detected. Must be A-F')
            return False, None

        return True, mapped_strength

    def parse_strength_config(self, config, name):
        parsing_error = False
        for port_config in config:
            self.__logger.debug('Parsing strength config "' + port_config + '"')
            port_config_array = port_config.split(':')
            if 2 != len(port_config_array):
                self.__logger.info('Invalid config "' + port_config + '" detected. Expected format: '
                                                                      'PORT:STRENGTH')
                self.__status_builder.unknown('Invalid config "' + port_config + '" detected. Expected format: '
                                                                                 'PORT:STRENGTH')
                parsing_error = True
                continue

            port = port_config_array[0]
            strength_status, strength = self.map_strength(port_config_array[1])
            if not strength_status:
                parsing_error = True
                self.__logger.info('Invalid config "' + port_config + '" detected. Expected format: '
                                                                      'PORT:STRENGTH')
                self.__status_builder.unknown('Invalid config "' + port_config + '" detected. Expected format: '
                                                                                 'PORT:STRENGTH')
                continue

            existing_config = self.__parsed_config.get(port, self.get_default_config())
            existing_strength = existing_config[name]['strength']
            if None == existing_strength or strength < existing_strength:
                self.__logger.debug('Setting strength to "' + str(strength) + '"')
                existing_config[name]['strength'] = strength

            self.__parsed_config[port] = existing_config

        return parsing_error

    def run(self, current, expected, port):

        least_strength = current['data']['least strength']
        self.check_least_strength(least_strength, port)
        for protocol in ['TLSv1.0', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']:
            self.__logger.debug('Compare protocol "' + protocol + '" of port "' + port + '".')
            existing_config = current['data'].get(protocol, {'ciphers': {'children': []}})
            expected_config = expected.get(protocol, None)

            self.check_ciphers(
                expected_config['ciphers'],
                existing_config['ciphers']['children'],
                protocol,
                port
            )
            self.check_cipher_strength(
                expected_config['strength'],
                existing_config['ciphers']['children'],
                protocol,
                port
            )

    def check_ciphers(self, expected_ciphers, existing_ciphers, protocol, port):

        if self.__ignoreciphername:
            return

        self.__logger.info('Compare ciphers of protocol "' + protocol + '" of port "' + port + '"')

        checked_ciphers = []
        for existing_cipher in existing_ciphers:
            self.__logger.debug('Check if existing cipher "' + existing_cipher['name'] + '" is expected in protocol "'
                                + protocol + '" of port "' + port + '"')
            if existing_cipher['name'] not in expected_ciphers:
                self.__logger.debug('Cipher "' + existing_cipher['name'] + '" was not expected in protocol "' +
                                    protocol + '" of port "' + port + '".')
                self.__status_builder.critical('Cipher "' + existing_cipher['name'] + '" was not expected in protocol "'
                                               + protocol + '" of port "' + port + '".')
                continue
            checked_ciphers.append(existing_cipher['name'])

        for expected_cipher in expected_ciphers:
            self.__logger.debug('Check if expected cipher "' + expected_cipher + '" is configured in protocol "' +
                                protocol + '" of port "' + port + '"')
            if expected_cipher not in checked_ciphers:
                self.__logger.debug('Cipher "' + expected_cipher + '" was expected but not found in protocol "' +
                                    protocol + '" of port "' + port + '".')
                self.__status_builder.warning('Cipher "' + expected_cipher +
                                              '" was expected but not found in protocol "' + protocol
                                              + '" of port "' + port + '".')

    def check_cipher_strength(self, expected_strength, existing_ciphers, protocol, port):

        if self.__ignorecipherstrength:
            return

        if None == expected_strength:
            self.__logger.info('Can\'t check cipher strength of protocol "' + protocol
                               + '" because no expected strength is set of port "' + port + '".')
            if 0 != len(existing_ciphers):
                self.__status_builder.unknown('Can\'t check cipher strength of protocol "' + protocol
                                              + '" because no expected strength is set of port "' + port + '".')
            return

        self.__logger.info('Compare ciphers strength of protocol "' + protocol + '" of port "' + port + '"')
        status, expected_strength_name = self.reverse_map_strength(expected_strength)

        for existing_cipher in existing_ciphers:
            status, existing_strength = self.map_strength(existing_cipher['strength'])
            if not status:
                self.__logger.debug('Unknown cipher "' + existing_cipher['strength'] + '" strength detected of port "'
                                    + port + '"')
                self.__status_builder.unknown('Unknown cipher "' + existing_cipher['strength']
                                              + '" strength detected of port "' + port + '"')
                continue

            self.__logger.debug('Check if existing cipher strength "' + existing_cipher['strength']
                                + '" is lower or equal to "' + expected_strength_name + '" of cipher "'
                                + existing_cipher['name'] + '" of port "' + port + '"')

            if existing_strength > expected_strength:
                self.__logger.debug('Cipher strength "' + existing_cipher['strength'] + '" is not lower or equal to "'
                                    + expected_strength_name + '" of cipher "' + existing_cipher['name']
                                    + '" of port "' + port + '"')
                self.__status_builder.critical('Cipher strength "' + existing_cipher['strength']
                                               + '" is not lower or equal to "' + expected_strength_name
                                               + '" of cipher "' + existing_cipher['name'] + '" of port "' + port + '"')

    def check_least_strength(self, least_strength, port):

        if self.__ignorestrength:
            return

        if None == self.__least_strength_overall:
            self.__logger.info('You have to set --least-strength-overall or --ignore-strength of port "' + port + '"')
            self.__status_builder.unknown('You have to set --least-strength-overall or --ignore-strength of port "'
                                          + port + '"')
            return

        expected_status, expected_strength = self.map_strength(self.__least_strength_overall)
        if not expected_status:
            self.__logger.info('You have to set --least-strength-overall to A-F of port "' + port + '"')
            self.__status_builder.unknown('You have to set --least-strength-overall to A-F of port "' + port + '"')
            return

        self.__logger.info('Compare ciphers strength "' + least_strength + '" is lower or equal "' +
                           self.__least_strength_overall + '" of port "' + port + '"')

        status, existing_strength = self.map_strength(least_strength)

        if existing_strength > expected_strength:
            self.__logger.info(
                'Ciphers strength "' + least_strength + '" is not lower or equal "' + self.__least_strength_overall +
                '" of port "' + port + '"')
            self.__status_builder.critical(
                'Ciphers strength "' + least_strength + '" is not lower or equal "' + self.__least_strength_overall +
                '" of port "' + port + '"')
