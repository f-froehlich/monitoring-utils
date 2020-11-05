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
import sys


class StatusBuilder:

    def __init__(self, logger):
        self.__logger = logger
        self.__success = []
        self.__warning = []
        self.__critical = []
        self.__unknown = []

    def success(self, message):
        logging.debug('Add success message: "' + message + '"')
        self.__success.append(message)

    def warning(self, message):
        logging.debug('Add warning message: "' + message + '"')
        self.__warning.append(message)

    def critical(self, message):
        logging.debug('Add critical message: "' + message + '"')
        self.__critical.append(message)

    def unknown(self, message):
        logging.debug('Add unknown message: "' + message + '"')
        self.__unknown.append(message)

    def exit(self):

        if 0 != len(self.__critical):
            for message in self.__critical:
                print('CRITICAL: ' + message)
            sys.exit(2)
        self.__logger.debug('No critical messages found')

        if 0 != len(self.__warning):
            for message in self.__warning:
                print('WARNING: ' + message)
            sys.exit(1)
        self.__logger.debug('No warning messages found')

        if 0 != len(self.__unknown):
            for message in self.__unknown:
                print('UNKNOWN: ' + message)
            sys.exit(3)
        self.__logger.debug('No unknown messages found')

        if 0 != len(self.__success):
            for message in self.__success:
                print('SUCCESS: ' + message)
            sys.exit(0)
        self.__logger.debug('No success messages found, exit with unknown')

        print('UNKNOWN: No status message found')
        sys.exit(3)
