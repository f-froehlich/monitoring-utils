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


import requests


class WebExecutor:

    def __init__(self, logger, parser, status_builder, client_key=None, client_cert=None, header=[], ssl=True,
                 port=None, domain=None, uri=None):

        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser
        self.__client_key = client_key
        self.__clinet_cert = client_cert
        self.__header = header
        self.__ssl = ssl
        self.__port = port
        self.__domain = domain
        self.__uri = uri

    def add_args(self):
        self.__parser.add_argument('-u', '--uri', dest='uri', type=str, help='URI to fetch', default='/')
        self.__parser.add_argument('-d', '--domain', dest='domain', type=str, help='Domain to fetch', required=True)
        self.__parser.add_argument('-p', '--port', dest='port', type=int, help='Port to fetch')
        self.__parser.add_argument('-s', '--ssl', dest='ssl', help='Use https', action='store_true')
        self.__parser.add_argument('--client-cert', dest='clientcert', type=str, help='Path to client certificate')
        self.__parser.add_argument('--client-key', dest='clientkey', type=str,
                                   help='Path to client certificate key file')
        self.__parser.add_argument('-H', '--header', dest='header', action='append', default=[],
                                   help='Header for request. Format: NAME=VALUE')

    def configure(self, args):

        self.__uri = args.uri
        self.__domain = args.domain
        self.__port = args.port
        self.__ssl = args.ssl
        self.__header = args.header
        self.__client_key = args.clientkey
        self.__clinet_cert = args.clientcert

    def run(self):
        self.__logger.info('Make a web request')
        proto = 'https' if self.__ssl else 'http'
        self.__logger.debug('Setup protocol to ' + proto)
        default_port = 443 if self.__ssl else 80
        port = self.__port if None != self.__port else default_port
        self.__logger.debug('Setup port to ' + str(port))

        headers = self.get_header()
        cert = self.get_client_cert_config()

        url = proto + '://' + self.__domain + ':' + str(port) + self.__uri
        self.__logger.debug('Make request to "' + url + '"')
        r = requests.get(url, headers=headers, cert=cert)
        r.encoding = 'utf-8'
        return r.text

    def get_header(self):
        headers = {}
        for header in self.__header:
            header_config = header.split("=")
            if 2 != len(header_config):
                self.__status_builder.unknown("Header must have the following format: NAME=VALUE. Invalid header '"
                                              + header + "' given.")
                self.__status_builder.exit()

            self.__logger.debug('Add header "' + header_config[0] + '" with value "' + header_config[1] + '"')
            headers[header_config[0]] = header_config[1]
        return headers

    def get_client_cert_config(self):
        cert = None
        if None is not self.__client_key and None is not self.__clinet_cert:
            self.__logger.debug('Add Client certificate')
            cert = (self.__clinet_cert, self.__client_key)
        elif None is not self.__client_key and None is self.__clinet_cert:
            self.__logger.debug('Key for client certificate authentication given but no certificate given')
            self.__status_builder.unknown(
                'If you specify a client certificate key, you have to specify a client certificate file.')
            self.__status_builder.exit()
        elif None is self.__client_key and None is not self.__clinet_cert:
            self.__logger.debug('Certificate for client certificate authentication given but no key given')
            self.__status_builder.unknown(
                'If you specify a client certificate, you have to specify a client certificate key file.')
            self.__status_builder.exit()
        return cert
