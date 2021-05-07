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
from datetime import datetime
from pathlib import Path

from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Plugin.Plugin import Plugin


class RebootRequired(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__exit_critical = None
        self.__ignore_if_scheduled = False

        Plugin.__init__(self, 'Check if a reboot is required')

    def add_args(self):
        self.__parser = self.get_parser()

        self.__parser.add_argument('--exit-critical', dest='exitcritical', required=False,
                                   action='store_true',
                                   help='Exit in critical state if reboot is required. If not set exit in warning state.')
        self.__parser.add_argument('--ignore-scheduled', dest='ignorescheduled', required=False,
                                   action='store_true',
                                   help='Ignore if a reboot is scheduled')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__exit_critical = args.exitcritical
        self.__ignore_if_scheduled = args.ignorescheduled

    def run(self):
        reboot_file = Path("/var/run/reboot-required")
        scheduled_file = Path("/run/systemd/shutdown/scheduled")
        self.__logger.debug('Check if file "/var/run/reboot-required" exist.')
        if reboot_file.is_file():
            self.__logger.debug('File "/var/run/reboot-required" exist.')
            if scheduled_file.exists() and scheduled_file.is_file():
                with open('/run/systemd/shutdown/scheduled', 'r') as file:
                    file_content = file.readlines()
                timestamp = None
                mode = None
                for line in file_content:
                    if "USEC=" in line:
                        timestamp = datetime.fromtimestamp(int(line.replace('USEC=', '').replace('\n', '')) / 1000000)
                    elif "MODE=" in line:
                        mode = line.replace('MODE=', '').replace('\n', '')

                output = Output(
                    f'Reboot required but scheduled at {timestamp.strftime("%Y-m-%d, %H:%M:%S")} in mode {mode}'
                )
                if self.__ignore_if_scheduled:
                    self.__status_builder.success(output)
                elif self.__exit_critical:
                    self.__status_builder.critical(output)
                else:
                    self.__status_builder.warning(output)

                return
            else:
                if self.__exit_critical:
                    self.__status_builder.critical('Reboot is required.')
                else:
                    self.__status_builder.warning('Reboot is required.')
                return

        self.__logger.debug('File "/var/run/reboot-required" does not exist.')
        self.__status_builder.success('No reboot is required.')


RebootRequired()
