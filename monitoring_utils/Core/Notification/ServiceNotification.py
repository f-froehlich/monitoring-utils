#!/usr/bin/python3
# -*- coding: utf-8

#  Monitoring monitoring-utils
#
#  Monitoring monitoring-utils are the background magic for my plugins, scripts and more
#
#  Copyright (c) 2020 Fabian Fröhlich <mail@confgen.org> https://icinga2.confgen.org
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


from monitoring_utils.Core.Notification.Notification import Notification


class ServiceNotification(Notification):

    def __init__(self, description):
        Notification.__init__(self, description)

        self.add_args()
        self.__servicename = None
        self.__servicedisplayname = None

    def add_args(self):
        self.__parser.add_argument('-e', '--servicename', dest='servicename', type=str, required=True,
                                   help='Name of service')
        self.__parser.add_argument('-u', '--servicedisplayname', dest='servicedisplayname', type=str, required=True,
                                   help='Displayname of service')

    def configure(self, args):
        Notification.configure(self, args)
        self.__servicename = args.servicename
        self.__servicedisplayname = args.servicedisplayname
