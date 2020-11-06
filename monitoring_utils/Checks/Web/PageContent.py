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


from monitoring_utils.Core.Executor.WebExecutor import WebExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class PageContent(Plugin):

    def __init__(self):

        self.__critical_content = None
        self.__warning_content = None
        self.__ok_content = None
        self.__web_executor = None
        Plugin.__init__(self, 'Check content of a page')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__web_executor = WebExecutor(logger=self.__logger, parser=self.__parser,
                                          status_builder=self.__status_builder)
        self.__web_executor.add_args()
        self.__parser.add_argument('-w', '--warning-content', dest='warningcontent', action='append', default=[],
                                   help='Warning content. Return warning state if at least one matched and no Critical content match')
        self.__parser.add_argument('-c', '--critical-content', dest='criticalcontent', action='append', default=[],
                                   help='Critical content. Return critical state if at least one matched')
        self.__parser.add_argument('-o', '--ok-content', dest='okcontent', action='append', default=[],
                                   help='OK content. Return OK state if at least one matched and no warning or critical content match')

    def configure(self, args):
        self.__web_executor.configure(args)
        self.__ok_content = args.okcontent
        self.__warning_content = args.warningcontent
        self.__critical_content = args.criticalcontent

    def run(self):
        content = self.__web_executor.run()
        self.parse_page_content(content)

    def parse_page_content(self, content):
        self.__logger.info('Check critical content')
        for e in self.__critical_content:
            print(self.__critical_content)
            self.__logger.debug('Check if "' + e + '" exists in response')
            if e in content:
                self.__logger.debug('Critical content "' + e + '" exists in response')
                self.__status_builder.critical("Found critical content '" + e + "' in response")

        self.__logger.info('Check warning content')
        for e in self.__warning_content:
            self.__logger.debug('Check if "' + e + '" exists in response')
            if e in content:
                self.__logger.debug('Warning content "' + e + '" exists in response')
                self.__status_builder.warning("Found warning content '" + e + "' in response")

        self.__logger.info('Check ok content')
        for e in self.__ok_content:
            self.__logger.debug('Check if "' + e + '" exists in response')
            if e in content:
                self.__logger.debug('OK content "' + e + '" exists in response')
                self.__status_builder.success("Found content '" + e + "' in response")
                return

        if 0 == len(self.__ok_content):
            self.__status_builder.unknown("No expected content match. Pleas specify at least one ok result.")
        else:
            self.__status_builder.critical("No expected content match.")
