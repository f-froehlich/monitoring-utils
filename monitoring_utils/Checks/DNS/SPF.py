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


from monitoring_utils.Core.Executor.DNSExecutor import DNSExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class SPF(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__expected = None
        self.__domain = None
        self.__resolver = None
        self.__executor = None

        Plugin.__init__(self, 'Check SPF policy')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-r', '--resolver', dest='resolver', default='1.1.1.1',
                                   help='Resolver for DNS Queries')
        self.__parser.add_argument('-e', '--expected', dest='expected', required=True,
                                   help='Expected SPF value')
        self.__parser.add_argument('-d', '--domain', dest='domain', required=True,
                                   help='Domain or zone to search')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__expected = args.expected
        self.__domain = args.domain
        self.__resolver = args.resolver
        self.__executor = DNSExecutor(self.__logger, self.__parser, self.__status_builder, self.__resolver)

    def run(self):

        self.check_spf()
        self.__status_builder.success('SPF passed')

    def check_spf(self):
        spf = self.__executor.resolve_SPF(self.__domain)

        if None == spf:
            return

        if 1 != len(spf):
            self.__status_builder.critical("Invalid SPF policy detected. You have multiple SPF policies specified")
            return

        if spf[0] != self.__expected:
            self.__status_builder.critical('Invalid SPF policy detected. Expected: "' + self.__expected + '" Got: "'
                                           + spf[0] + '"')
