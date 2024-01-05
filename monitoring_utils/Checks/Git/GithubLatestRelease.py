#!/usr/bin/python3
# -*- coding: utf-8
import json

from monitoring_utils.Core.Executor.WebExecutor import WebExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


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


class GithubLatestRelease(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__expected = None
        self.__repository = None
        self.__executor = None

        Plugin.__init__(self, 'Check latest github release')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument(
                '-e', '--expected', dest='expected', required=True,
                help='Expected release value'
        )
        self.__parser.add_argument(
                '-r', '--repository', dest='repository', required=True,
                help='Github repository url'
        )

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__expected = args.expected
        self.__repository = args.repository
        repo_name = '/'.join(self.__repository.split('/')[-2:])
        self.__executor = WebExecutor(
                self.__logger,
                self.__parser,
                self.__status_builder,
                domain="api.github.com",
                uri=f"/repos/{repo_name}/releases/latest"
        )

    def run(self):

        release_info = json.loads(self.__executor.run_get())

        if release_info['tag_name'] == self.__expected:
            self.__status_builder.success('Version matched')
        else:
            self.__status_builder.critical(
                f"Version don't match. Expected '{self.__expected}' but got '{release_info['tag_name']}'\n\n"
                f"Checkout the release at '{release_info['html_url']}'"
                )

