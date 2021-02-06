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


from os import path

from monitoring_utils.Core.Plugin.Plugin import Plugin


class DS18B20(Plugin):

    def __init__(self):
        self.__warn_inactive = None
        self.__name = None
        self.__device = None
        self.__path = None
        self.__warning = None
        self.__critical = None

        Plugin.__init__(self, 'Check DS18B20 temperature')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-d', '--device', dest='device', required=True,
                                   help='Device of DS18B20 sensor e.g. 28-0316b3a722ff (must be in prefix path folder)')
        self.__parser.add_argument('-n', '--name', dest='name', default=None,
                                   help='Custom name of sensor')
        self.__parser.add_argument('-p', '--path', dest='path', default='/sys/bus/w1/devices/',
                                   help='Prefix path, which contains the device')
        self.__parser.add_argument('-w', '--warning', dest='warning', type=float,
                                   default=28.0, help='Warning temperature (degree celsius)')
        self.__parser.add_argument('-c', '--critical', dest='critical', type=float,
                                   default=35.0, help='Critical temperature (degree celsius)')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__device = args.device
        self.__name = args.name
        self.__path = args.path
        self.__warning = args.warning
        self.__critical = args.critical

    def run(self):

        self.check_requirements()

        temperature = self.get_temperature()
        perfdata = self.get_name() + '=' + str(temperature) + ';' + str(self.__warning) + ';' + str(
            self.__critical) + ';'

        if temperature >= self.__critical:
            self.__status_builder.critical(
                'Sensor "{name}" has critical temperature of "{temperature}"°C;|{perfdata}'
                    .format(name=self.get_name(), temperature=temperature, perfdata=perfdata))
        elif temperature >= self.__warning:
            self.__status_builder.warning(
                'Sensor "{name}" has warning temperature of "{temperature}"°C;|{perfdata}'
                    .format(name=self.get_name(), temperature=temperature, perfdata=perfdata))
        else:
            self.__status_builder.success(
                'Sensor "{name}" has temperature of "{temperature}"°C;|{perfdata}'
                    .format(name=self.get_name(), temperature=temperature, perfdata=perfdata))

    def check_requirements(self):
        if not path.exists(self.__path):
            self.__status_builder.critical('Device path "{path}" does not exist'.format(path=self.__path))
            self.__status_builder.exit()

        if not path.isdir(self.__path):
            self.__status_builder.critical('Device path "{path}" is not a directory'.format(path=self.__path))
            self.__status_builder.exit()

        if not path.exists(self.__path + '/' + self.__device):
            self.__status_builder.critical('Device "{device}" does not exist'.format(device=self.__device))
            self.__status_builder.exit()

        if not path.isdir(self.__path + '/' + self.__device) \
                or not path.exists(self.__path + '/' + self.__device + '/temperature') \
                or not path.isfile(self.__path + '/' + self.__device + '/temperature') \
                or not path.exists(self.__path + '/' + self.__device + '/name') \
                or not path.isfile(self.__path + '/' + self.__device + '/name'):
            self.__status_builder.critical('Device "{device}" is not a DS18B20 sensor'.format(device=self.__device))
            self.__status_builder.exit()

    def get_temperature(self):

        with open(self.__path + self.__device + '/temperature') as temperature_file:
            lines = temperature_file.readlines()

        if len(lines) < 1:
            self.__status_builder.critical('Device "{device}" is not a DS18B20 sensor'.format(device=self.__device))
            self.__status_builder.exit()

        return int(lines[0].replace('\n', '')) / 1000

    def get_name(self):

        if None != self.__name:
            return self.__name

        with open(self.__path + self.__device + '/name') as name_file:
            lines = name_file.readlines()
        if len(lines) < 1:
            self.__status_builder.critical('Device "{device}" is not a DS18B20 sensor'.format(device=self.__device))
            self.__status_builder.exit()

        self.__name = lines[0].replace('\n', '')

        return self.__name
