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


class Notification:

    def __init__(self, description):
        self.__parser = argparse.ArgumentParser(description=description)
        self.__logger = Logger(self.__parser)
        self.__status_builder = StatusBuilder(self.__logger)
        self.__signals = Signals(self.__parser, self.__logger, self.__status_builder)
        self.add_args()

        self.__date = None
        self.__hostname = None
        self.__display_name = None
        self.__output = None
        self.__state = None
        self.__hostaddress = None
        self.__hostaddress6 = None
        self.__author = None
        self.__comment = None
        self.__url = None
        self.__type = None
        self.__notification_from = None
        self.__short = False

        args = self.__parser.parse_args()
        self.__logger.configure(args)
        self.__signals.configure(args)
        self.configure(args)
        self.run()
        self.__status_builder.exit()

    def add_args(self):
        self.__parser.add_argument('-d', '--date', dest='date', type=str, required=True, help='Date of notification')
        self.__parser.add_argument('-l', '--hostname', dest='hostname', type=str, required=True, help='Hostname')
        self.__parser.add_argument('-n', '--display-name', dest='displayname', type=str, required=True,
                                   help='Host display name')
        self.__parser.add_argument('-o', '--output', dest='output', type=str, required=True,
                                   help='Output of service')
        self.__parser.add_argument('-s', '--state', dest='state', type=str, required=True,
                                   help='State of service')
        self.__parser.add_argument('-t', '--type', dest='type', type=str, required=True, help='Type of Notification')

        self.__parser.add_argument('-4', '--host-address', dest='hostaddress', type=str, help='IPv4 address of host')
        self.__parser.add_argument('-6', '--host-address6', dest='hostaddress6', type=str, help='IPv6 address of host')
        self.__parser.add_argument('-a', '--author', dest='author', type=str, help='Author of notification')
        self.__parser.add_argument('-c', '--comment', dest='comment', type=str, help='Comment of notification')
        self.__parser.add_argument('-i', '--url', dest='url', type=str, help='URL of notification')
        self.__parser.add_argument('-f', '--from', dest='notificationfrom', type=str, help='URL of notification')
        self.__parser.add_argument('--short', dest='short', action='store_true', help='Only send a short summary')

    def configure(self, args):
        self.__date = args.date
        self.__hostname = args.hostname
        self.__display_name = args.displayname
        self.__output = args.output
        self.__state = args.state
        self.__hostaddress = args.hostaddress
        self.__hostaddress6 = args.hostaddress6
        self.__author = args.author
        self.__comment = args.comment
        self.__url = args.url
        self.__type = args.type
        self.__notification_from = args.notificationfrom
        self.__short = args.short

    def run(self):
        self.__status_builder.critical('Plugin have to override run method')
        self.__status_builder.exit()

    def get_logger(self):
        return self.__logger

    def get_parser(self):
        return self.__parser

    def get_status_builder(self):
        return self.__status_builder

    def get_date(self):
        return self.__date

    def get_state(self):
        return self.__state

    def get_author(self):
        return self.__author

    def get_comment(self):
        return self.__comment

    def get_url(self):
        return self.__url

    def get_short(self):
        return self.__short

    def get_hostaddress(self):
        return self.__hostaddress

    def get_hostaddress6(self):
        return self.__hostaddress6

    def get_output(self):
        return self.__output

    def get_hostname(self):
        return self.__hostname

    def get_display_name(self):
        return self.__display_name

    def get_message(self):
        self.__logger.info('Create host message')
        message = """***** {displayname} is {state} *****
Host:    {hostname}
When:   {date}

Info:    {output}
""".format(
            displayname=self.__display_name,
            state=self.__state,
            output=self.__output,
            hostname=self.__hostname,
            date=self.__date
        )

        if self.__short:
            return message

        return message + self.get_optional_messagedata()

    def get_optional_messagedata(self):
        message = ''
        self.__logger.info('Add additional information')

        if None != self.__hostaddress:
            self.__logger.debug('Add IPv4')
            message += 'IPv4:    {ipv4}\n'.format(ipv4=self.__hostaddress)
        if None != self.__hostaddress6:
            self.__logger.debug('Add IPv6')
            message += 'IPv6:    {ipv6}\n'.format(ipv6=self.__hostaddress6)
        if None != self.__comment:
            self.__logger.debug('Add Comment')
            message += 'Comment:    {comment}\n'.format(comment=self.__comment)
        if None != self.__url:
            self.__logger.debug('Add url')
            message += 'URL:    {url}\n'.format(url=self.__url)
        if None != self.__notification_from:
            self.__logger.debug('Add from')
            message += 'From:    {notefrom}\n'.format(notefrom=self.__notification_from)

        return message
