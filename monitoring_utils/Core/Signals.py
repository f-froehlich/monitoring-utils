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


import signal


class Signals:

    def __init__(self, parser, logger, status_builder):
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser
        signal.signal(signal.SIGALRM, self.timeout_handler)
        self.__timeout = 10
        self.add_args()

    def add_args(self):
        self.__parser.add_argument('--timeout', dest='timeout', default=self.__timeout, type=int,
                                   help='Timeout to exit this script')

    def configure(self, args):
        self.__timeout = args.timeout
        self.__logger.debug('Setting up timeout signal to ' + str(self.__timeout) + ' seconds.')
        signal.alarm(self.__timeout)

    def timeout_handler(self, signum, frame):
        self.__logger.info('Timeout of ' + str(self.__timeout) + ' seconds reached.')
        self.__status_builder.unknown('Timeout of ' + str(self.__timeout) + ' seconds reached.')
        self.__status_builder.exit()
