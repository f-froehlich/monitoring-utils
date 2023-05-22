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

from monitoring_utils.Core.Notification.ServiceNotification import ServiceNotification as BaseServiceNotification


class MailServiceNotification(BaseServiceNotification):

    def __init__(self, description: str):
        self.__smtp_executor = None
        BaseServiceNotification.__init__(self, description)
        self.__subject = None

    def add_args(self):
        BaseServiceNotification.add_args(self)
        self.__parser = self.get_parser()

        self.__parser.add_argument('--subject', dest='subject', type=str, help='Subject template',
                                   default='{servicedisplayname} is {state} on host {displayname}')

    def configure(self, args):
        BaseServiceNotification.configure(self, args)
        self.__subject = args.subject

    def get_subject(self):
        return self.__subject.format(
            displayname=self.get_display_name(),
            state=self.get_state(),
            output=self.get_output(),
            hostname=self.get_hostname(),
            date=self.get_date(),
            ipv4=self.get_hostaddress(),
            ipv6=self.get_hostaddress6(),
            comment=self.get_comment(),
            url=self.get_url(),
            notefrom=self.get_notification_from(),
            servicedisplayname=self.get_service_display_name(),
            servicename=self.get_service_name(),
        )
