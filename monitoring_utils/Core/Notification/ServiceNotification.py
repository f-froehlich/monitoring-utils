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


from monitoring_utils.Core.Notification.Notification import Notification


class ServiceNotification(Notification):

    def __init__(self, description):
        self.__servicename = None
        self.__servicedisplayname = None
        Notification.__init__(self, description)

    def add_args(self):
        Notification.add_args(self)
        self.__parser = self.get_parser()
        self.__parser.add_argument('-e', '--servicename', dest='servicename', type=str, required=True,
                                   help='Name of service')
        self.__parser.add_argument('-u', '--servicedisplayname', dest='servicedisplayname', type=str, required=True,
                                   help='Displayname of service')

    def configure(self, args):
        Notification.configure(self, args)
        self.__servicename = args.servicename
        self.__servicedisplayname = args.servicedisplayname

    def get_service_name(self):
        return self.__servicename

    def get_service_display_name(self):
        return self.__servicedisplayname

    def get_message(self):
        self.__logger.info('Create service message')
        message = """***** {servicedisplayname} is {state} on Host {displayname} *****
Service:    {servicedisplayname} ({servicename})
Host:    {displayname} ({hostname})
When:   {date}

Info:    {output}
""".format(
            servicedisplayname=self.get_service_display_name(),
            servicename=self.get_service_name(),
            displayname=self.get_display_name(),
            state=self.get_state(),
            output=self.get_output(),
            hostname=self.get_hostname(),
            date=self.get_date()
        )

        if self.get_short():
            return message

        return message + self.get_optional_messagedata()
