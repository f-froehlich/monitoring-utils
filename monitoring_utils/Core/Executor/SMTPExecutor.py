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

from email.message import EmailMessage
from smtplib import SMTP_SSL, SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPExecutor:

    def __init__(self, parser, logger, status_builder, user=None, secret=None, sender=None, host=None, port=None,
                 usessl=False, usestarttls=False, recipients=[]):
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser
        self.__recipients = recipients
        self.__secret = secret
        self.__sender = sender
        self.__client = None
        self.__user = user
        self.__host = host
        self.__port = port
        self.__use_ssl = usessl
        self.__use_starttls = usestarttls

    def add_args(self):
        self.__parser.add_argument('-U', '--user', dest='user', type=str, help='Username to login', required=False)
        self.__parser.add_argument('-S', '--secret', dest='secret', type=str, help='Secret for login', required=False)
        self.__parser.add_argument('-H', '--host', dest='host', type=str, help='Hostname or IP of SMTP server',
                                   required=True)
        self.__parser.add_argument('-p', '--port', dest='port', type=int, help='Port of SMTP server',
                                   required=True)
        self.__parser.add_argument('-F', '--sender', dest='sender', type=str, help='Sender email', required=True)
        self.__parser.add_argument('-r', '--recipient', dest='recipients', action='append', default=[],
                                   help='Recipient email addresses')
        self.__parser.add_argument('--use-ssl', dest='usessl', required=False, action='store_true',
                                   help='Use SMTPS')
        self.__parser.add_argument('--use-starttls', dest='usestarttls', required=False, action='store_true',
                                   help='Use start TLS')

    def configure(self, args):
        self.__user = args.user
        self.__secret = args.secret
        self.__sender = args.sender
        self.__host = args.host
        self.__port = args.port
        self.__use_ssl = args.usessl
        self.__use_starttls = args.usestarttls

        for recipient in args.recipients:
            self.__recipients.append(recipient)

        if self.__user is None and self.__secret is not None:
            self.__status_builder.critical("If secret is set you have to set user as well")
            self.__status_builder.exit()
        if self.__user is not None and self.__secret is None:
            self.__status_builder.critical("If user is set you have to set secret as well")
            self.__status_builder.exit()

    def send(self, subject, message):

        self.__logger.info('Sending message:\n Subject: ' + subject + '\n body: ' + message)
        for recipient in self.__recipients:
            # Craft the email using email.message.EmailMessage
            email_message = MIMEMultipart()
            email_message.add_header('To', ', '.join(self.__recipients))
            email_message.add_header('From', self.__sender)
            email_message.add_header('Subject', subject)
            email_message.add_header('X-Priority', '1')  # Urgency, 1 highest, 5 lowest
            html_part = MIMEText(message, 'html')
            email_message.attach(html_part)

            if self.__use_ssl:
                # Connect, authenticate, and send mail
                smtp_server = SMTP_SSL(self.__host, port=self.__port)
            elif self.__use_starttls:
                smtp_server = SMTP(self.__host, port=self.__port)
                smtp_server.starttls()
            else:
                smtp_server = SMTP(self.__host, port=self.__port)

            if None is not self.__user:
                smtp_server.login(self.__user, self.__secret)

            smtp_server.sendmail(self.__sender, recipient, email_message.as_bytes())

            # Disconnect
            smtp_server.quit()
