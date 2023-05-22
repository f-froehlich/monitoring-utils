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

from monitoring_utils.Core.Executor.SMTPExecutor import SMTPExecutor
from monitoring_utils.Core.Notification.MailServiceNotification import \
    MailServiceNotification as BaseMailServiceNotification


class ServiceNotification(BaseMailServiceNotification):

    def __init__(self):
        self.__smtp_executor = None
        BaseMailServiceNotification.__init__(self, 'Send a service-notification via SMTP')
        self.__smtp_executor = None

    def add_args(self):
        BaseMailServiceNotification.add_args(self)
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__smtp_executor = SMTPExecutor(logger=self.__logger, parser=self.__parser,
                                            status_builder=self.__status_builder)
        self.__smtp_executor.add_args()

    def configure(self, args):
        BaseMailServiceNotification.configure(self, args)
        self.__smtp_executor.configure(args)

    def run(self):
        self.__smtp_executor.send(self.get_subject(), self.get_message())
        self.__status_builder.success('Send service notification successful')
