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


class Plugin:

    def __init__(self, description):
        self.__parser = argparse.ArgumentParser(description=description)
        self.__logger = Logger(self.__parser)
        self.__status_builder = StatusBuilder(self.__logger)
        self.__signals = Signals(self.__parser, self.__logger, self.__status_builder)

        self.add_args()

        args = self.__parser.parse_args()
        self.__logger.configure(args)
        self.__signals.configure(args)
        self.configure(args)
        self.run()
        self.__status_builder.exit()

    def add_args(self):
        self.__status_builder.critical('Plugin have to override add_args method')
        self.__status_builder.exit()

    def configure(self, args):
        self.__status_builder.critical('Plugin have to override configure method')
        self.__status_builder.exit()

    def run(self):
        self.__status_builder.critical('Plugin have to override run method')
        self.__status_builder.exit()

    def get_logger(self):
        return self.__logger

    def get_parser(self):
        return self.__parser

    def get_status_builder(self):
        return self.__status_builder
