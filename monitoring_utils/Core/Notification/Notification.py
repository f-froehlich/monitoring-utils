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


import argparse

from monitoring_utils.Core.Logger import Logger
from monitoring_utils.Core.Signals import Signals
from monitoring_utils.Core.StatusBuilder import StatusBuilder


class Notification:

    def __init__(self, description):
        self.__parser = argparse.ArgumentParser(description=description)
        self.__logger = Logger(self.__parser)
        self.__status_builder = StatusBuilder(self.__logger)
        self.__signals = Signals(self.__parser, self.__logger, self.__status_builder)
        self.add_args()

        self.__date = None
        self.__hostname = None
        self.__displayname = None
        self.__output = None
        self.__servicestate = None
        self.__hostaddress = None
        self.__hostaddress6 = None
        self.__author = None
        self.__comment = None
        self.__url = None
        self.__type = None
        self.__notificationfrom = None

    def add_args(self):
        self.__parser.add_argument('-d', '--date', dest='date', type=str, required=True, help='Date of notification')
        self.__parser.add_argument('-l', '--hostname', dest='hostname', type=str, required=True, help='Hostname')
        self.__parser.add_argument('-n', '--display-name', dest='displayname', type=str, required=True,
                                   help='Host display name')
        self.__parser.add_argument('-o', '--output', dest='output', type=str, required=True,
                                   help='Output of service')
        self.__parser.add_argument('-s', '--service-state', dest='servicestate', type=str, required=True,
                                   help='State of service')
        self.__parser.add_argument('-t', '--type', dest='type', type=str, required=True, help='Type of Notification')

        self.__parser.add_argument('-4', '--host-address', dest='hostaddress', type=str, help='IPv4 address of host')
        self.__parser.add_argument('-6', '--host-address6', dest='hostaddress6', type=str, help='IPv6 address of host')
        self.__parser.add_argument('-a', '--author', dest='author', type=str, help='Author of notification')
        self.__parser.add_argument('-c', '--comment', dest='comment', type=str, help='Comment of notification')
        self.__parser.add_argument('-u', '--url', dest='url', type=str, help='URL of notification')
        self.__parser.add_argument('-f', '--from', dest='notificationfrom', type=str, help='URL of notification')

    def configure(self, args):
        self.__date = args.date
        self.__hostname = args.hostname
        self.__displayname = args.diyplayname
        self.__output = args.output
        self.__servicestate = args.servicestate
        self.__hostaddress = args.hostaddress
        self.__hostaddress6 = args.hostaddress6
        self.__author = args.author
        self.__comment = args.comment
        self.__url = args.url
        self.__type = args.type
        self.__notificationfrom = args.notificationfrom
