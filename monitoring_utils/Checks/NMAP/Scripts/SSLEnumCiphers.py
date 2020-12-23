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
from nmap_scan.Scripts.SSLEnumCiphers import CipherCompare


class SSLEnumCiphers:

    def __init__(self, logger, status_builder, parser):
        self.__parser = parser
        self.__logger = logger
        self.__status_builder = status_builder
        self.__open_ports = []
        self.__config = {}
        self.__single_host = False

        self.__ignoreciphername = None
        self.__ignoreprotocolstrength = None
        self.__ignoreportstrength = None

    def set_parsed_config(self, config):
        self.__config = config

    def get_config_for_host(self, ip):
        return self.__config.get(ip, None)

    def add_args(self):

        self.__parser.add_argument('--allowed-cipher', dest='allowedciphers', action='append',
                                   help='Allowed chippers. Format: HOST/PORT/PROTOCOL/NAME[,NAME[,NAME ...]] '
                                        'or PORT/PROTOCOL/NAME[,NAME[,NAME ...]] if "--single-host" is set.',
                                   default=[])

        self.__parser.add_argument('--least-protocol-strength', dest='leastprotocolstrength', default=[],
                                   action='append',
                                   help='Least strength of PROTOCOL chippers. Format: HOST/PORT/PROTOCOL/STRENGTH'
                                        'or PORT/PROTOCOL/STRENGTH if "--single-host" is set.')

        self.__parser.add_argument('--least-port-strength', dest='leastportstrength', default=[], action='append',
                                   help='Least strength of chippers. Format: HOST/PORT/STRENGTH'
                                        'or PORT/STRENGTH if "--single-host" is set.')

        # self.__parser.add_argument('--least-strength-overall', dest='leaststrengthoverall', default='B', type=str,
        #                            help='Least strength of chippers over all ports.')

        self.__parser.add_argument('-iCN', '--ignore-cipher-name', dest='ignoreciphername', required=False,
                                   action='store_true', help='Ignore the cipher name comparison')
        self.__parser.add_argument('-iPS', '--ignore-protocol-strength', dest='ignoreprotocolstrength',
                                   required=False,
                                   action='store_true',
                                   help='Ignore the least cipher strength comparison for protocols')
        self.__parser.add_argument('-iS', '--ignore-strength', dest='ignoreportstrength', required=False,
                                   action='store_true', help='Ignore the strength comparison for ports')

    def configure(self, args):

        self.__ignoreprotocolstrength = args.ignoreprotocolstrength
        self.__ignoreciphername = args.ignoreciphername
        self.__ignoreportstrength = args.ignoreportstrength
        self.__single_host = args.singlehost

        if self.__ignoreciphername and self.__ignoreprotocolstrength and self.__ignoreportstrength:
            self.__status_builder.unknown('You set --ignore-cipher-name, --ignore-cipher-strength and '
                                          '--ignore-port-strength so no check can be executed.')
            self.__status_builder.exit()

        if self.__single_host:
            if len(args.hosts) != 1:
                self.__status_builder.unknown('You set --single-host but you don\'t set exactly once --host. Can\'t '
                                              'proceed with this configuration.')
                self.__status_builder.exit()

            host = args.hosts[0]
            allowedciphers = []
            leastprotocolstrength = []
            leastportstrength = []

            for a in args.allowedciphers:
                allowedciphers.append(host + '/' + a)

            for a in args.leastprotocolstrength:
                leastprotocolstrength.append(host + '/' + a)

            for a in args.leastportstrength:
                leastportstrength.append(host + '/' + a)

            self.parse_allowed_ciphers(allowedciphers)
            self.parse_protocol_strength(leastprotocolstrength)
            self.parse_port_strength(leastportstrength)

        else:
            self.parse_allowed_ciphers(args.allowedciphers)
            self.parse_protocol_strength(args.leastprotocolstrength)
            self.parse_port_strength(args.leastportstrength)

    def execute(self, port, script, config):
        self.check_cipher_names(port, script, config)
        self.check_cipher_strength(port, script, config)
        self.check_port_strength(port, script, config)

    def parse_allowed_ciphers(self, configs):
        for config in configs:
            self.__logger.debug('Parsing config "{config}"'.format(config=config))
            config_array = config.split('/')
            if 4 != len(config_array):
                self.__status_builder.unknown('Invalid config "{config}" detected. Expected format: '
                                              '"HOST/PORT/PROTOCOL/NAME[,NAME[,NAME ...]]" '
                                              'or "PORT/PROTOCOL/NAME[,NAME[,NAME ...]]" if "--single-host" is set.'.format(
                    config=config))

            host_config = self.__config.get(config_array[0], {})
            port_config = host_config.get(int(config_array[1]), {})
            port_protocol_config = port_config.get('protocol', {})
            protocol_config = port_protocol_config.get(config_array[2].lower(), {})
            protocol_cipher_config = protocol_config.get('cipher', [])
            for cipher in config_array[3].split(','):
                if cipher not in protocol_config:
                    protocol_cipher_config.append(cipher)
            protocol_config['cipher'] = protocol_cipher_config
            port_protocol_config[config_array[2].lower()] = protocol_config
            port_config['protocol'] = port_protocol_config
            host_config[int(config_array[1])] = port_config
            self.__config[config_array[0]] = host_config

    def parse_protocol_strength(self, configs):
        for config in configs:
            self.__logger.debug('Parsing config "{config}"'.format(config=config))
            config_array = config.split('/')
            if 4 != len(config_array):
                self.__status_builder.unknown('Invalid config "{config}" detected. Expected format: '
                                              '"HOST/PORT/PROTOCOL/STRENGTH"'
                                              'or "PORT/PROTOCOL/STRENGTH" if "--single-host" is set'.format(
                    config=config))

            host_config = self.__config.get(config_array[0], {})
            port_config = host_config.get(int(config_array[1]), {})
            port_protocol_config = port_config.get('protocol', {})
            protocol_config = port_protocol_config.get(config_array[2].lower(), {})
            protocol_strength_config = protocol_config.get('strength', None)
            if None != protocol_strength_config:
                if CipherCompare.a_lower_b(config_array[3], protocol_strength_config):
                    protocol_strength_config = config_array[3]
            else:
                protocol_strength_config = config_array[3]

            protocol_config['strength'] = protocol_strength_config
            port_config[config_array[2].lower()] = protocol_config
            port_protocol_config[config_array[2].lower()] = protocol_config
            port_config['protocol'] = port_protocol_config
            host_config[int(config_array[1])] = port_config
            self.__config[config_array[0]] = host_config

    def parse_port_strength(self, configs):
        for config in configs:
            self.__logger.debug('Parsing config "{config}"'.format(config=config))
            config_array = config.split('/')
            if 3 != len(config_array):
                self.__status_builder.unknown('Invalid config "{config}" detected. Expected format: '
                                              '"HOST/PORT/STRENGTH"'
                                              'or "PORT/STRENGTH" if "--single-host" is set'.format(config=config))

            host_config = self.__config.get(config_array[0], {})
            port_config = host_config.get(int(config_array[1]), {})
            protocol_strength_config = port_config.get('strength', None)
            if None != protocol_strength_config:
                if CipherCompare.a_lower_b(config_array[2], protocol_strength_config):
                    protocol_strength_config = config_array[2]
            else:
                protocol_strength_config = config_array[2]

            port_config['strength'] = protocol_strength_config
            host_config[int(config_array[1])] = port_config
            self.__config[config_array[0]] = host_config

    def check_cipher_names(self, port, script, config):

        if self.__ignoreciphername:
            return

        protocols = script.get_protocols()
        for protocol in protocols:

            protocol_config = config.get('protocol', None)
            if None == protocol_config:
                self.__status_builder.unknown(
                    'No configuration for port "{port}" set.'
                        .format(protocol=protocol, port=port.get_port())
                )
                continue
            port_config = protocol_config.get(protocol, None)
            if None == port_config:
                self.__status_builder.critical(
                    'Protocol version "{protocol}" of port "{port}" was not expected.'
                        .format(protocol=protocol, port=port.get_port())
                )
                continue

            allowed_ciphers = port_config.get('cipher', [])
            existing_ciphers = []
            for current_cipher in protocols[protocol].get_ciphers():
                existing_ciphers.append(current_cipher.get_name())
                if current_cipher.get_name() not in allowed_ciphers:
                    self.__status_builder.critical(
                        'Cipher "{cipher}" was not expected in protocol "{protocol}" of port "{port}".'
                            .format(cipher=current_cipher.get_name(), protocol=protocol, port=port.get_port())
                    )

            for allowed_cipher in allowed_ciphers:
                if allowed_cipher not in existing_ciphers:
                    self.__status_builder.warning(
                        'Cipher "{cipher}" was expected in protocol "{protocol}" of port "{port}" but was not found.'
                            .format(cipher=allowed_cipher, protocol=protocol, port=port.get_port())
                    )

        for allowed_protocol in config:
            existing_protocol = protocols.get(allowed_protocol, None)
            if None == existing_protocol:
                self.__status_builder.warning(
                    'Protocol version "{protocol}" of port "{port}" was expected but was not found.'
                        .format(protocol=allowed_protocol, port=port.get_port())
                )

    def check_cipher_strength(self, port, script, config):
        if self.__ignoreprotocolstrength:
            return

        protocols = script.get_protocols()
        for protocol in protocols:
            protocol_config = config.get('protocol', None)
            if None == protocol_config:
                self.__status_builder.unknown(
                    'No configuration for port "{port}" set.'
                        .format(protocol=protocol, port=port.get_port())
                )
                continue
            port_config = protocol_config.get(protocol, None)
            if None == port_config:
                self.__status_builder.critical(
                    'Protocol version "{protocol}" of port "{port}" was not expected.'
                        .format(protocol=protocol, port=port.get_port())
                )
                continue
            allowed_strength = port_config.get('strength', None)

            if not CipherCompare.a_lower_equals_b(protocols[protocol].get_least_strength(), allowed_strength):
                self.__status_builder.critical(
                    'Least cipher strength of protocol version "{protocol}" of port "{port}" does not match. '
                    'Expected: "{expected}", got: "{got}"'
                        .format(protocol=protocol, port=port.get_port(), expected=allowed_strength,
                                got=protocols[protocol].get_least_strength())
                )

        for allowed_protocol in config:
            existing_protocol = protocols.get(allowed_protocol, None)
            if None == existing_protocol:
                self.__status_builder.critical(
                    'Strength of protocol version "{protocol}" of port "{port}" was expected but was not found.'
                        .format(protocol=allowed_protocol, port=port.get_port())
                )

    def check_port_strength(self, port, script, config):
        if self.__ignoreportstrength:
            return

        allowed_strength = config.get('strength', None)
        if None == allowed_strength:
            self.__status_builder.unknown(
                'No strength configuration for port "{port}" set. Either ignore the port strength check or set up a '
                'configuration for the port.'
                    .format(port=port.get_port())
            )
            return

        if not CipherCompare.a_lower_equals_b(script.get_least_strength(), allowed_strength):
            self.__status_builder.critical(
                'Least cipher strength of port "{port}" does not match. '
                'Expected: "{expected}", got: "{got}"'
                    .format(port=port.get_port(), expected=allowed_strength,
                            got=script.get_least_strength())
            )
