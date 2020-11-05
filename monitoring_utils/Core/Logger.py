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


import logging


class Logger:

    def __init__(self, parser):
        self.__parser = parser
        self.__verbose = False
        self.__debug = False
        self.add_args()

    def add_args(self):
        self.__parser.add_argument('--verbose', dest='verbose', action='store_true', help='Output more messages')
        self.__parser.add_argument('--debug', dest='debug', action='store_true', help='Output debug messages')

    def configure(self, args):
        self.__debug = args.debug
        self.__verbose = args.verbose
        if self.__debug:
            logging.basicConfig(level=logging.DEBUG)
        elif self.__verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)

    def info(self, message):
        logging.info(message)

    def debug(self, message):
        logging.debug(message)
