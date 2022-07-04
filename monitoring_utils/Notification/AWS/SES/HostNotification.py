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

from monitoring_utils.Core.Executor.AWSSESExecutor import AWSSESExecutor
from monitoring_utils.Core.Notification.Notification import Notification


class HostNotification(Notification):

    def __init__(self):
        self.__aws_executor = None
        Notification.__init__(self, 'Send a host-notification via AWS SES API')
        self.__subject = None

    def add_args(self):
        Notification.add_args(self)
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__aws_executor = AWSSESExecutor(logger=self.__logger, parser=self.__parser,
                                             status_builder=self.__status_builder)
        self.__aws_executor.add_args()

        self.__parser.add_argument('--subject', dest='subject', type=str, help='Subject template',
                                   default='{displayname} is {state}')


    def configure(self, args):
        Notification.configure(self, args)
        self.__aws_executor.configure(args)
        self.__subject = args.subject

    def run(self):
        subject = self.__subject.format(
            displayname=self.get_display_name(),
            state=self.get_state(),
            output=self.get_output(),
            hostname=self.get_hostname(),
            date=self.get_date(),
            ipv4=self.get_hostaddress(),
            ipv6=self.get_hostaddress6(),
            comment=self.get_comment(),
            url=self.get_url(),
            notefrom=self.get_notification_from()
        )
        self.__aws_executor.send(subject, self.get_message())
        self.__status_builder.success('Send host notification successful')
