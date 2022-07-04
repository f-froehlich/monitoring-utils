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

import boto3
from botocore.exceptions import ClientError


class AWSSESExecutor:

    def __init__(self, parser, logger, status_builder, key_id=None, secret=None, sender=None, region='us-west-2',
                 recipients=[]):
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser
        self.__recipients = recipients
        self.__key_id = key_id
        self.__secret = secret
        self.__sender = sender
        self.__region = region
        self.__client = None

    def add_args(self):
        self.__parser.add_argument('-k', '--key-id', dest='keyid', type=str, help='ID of AWS SES key', required=True)
        self.__parser.add_argument('-S', '--secret', dest='secret', type=str, help='Secret of AWS SES key',
                                   required=True)
        self.__parser.add_argument('-F', '--sender', dest='sender', type=str, help='SES sender email', required=True)
        self.__parser.add_argument('-R', '--region', dest='region', type=str, help='SES region default: us-west-2',
                                   default='us-west-2')
        self.__parser.add_argument('-r', '--recipient', dest='recipients', action='append', default=[],
                                   help='Recipient email addresses')

    def configure(self, args):
        self.__key_id = args.keyid
        self.__secret = args.secret
        self.__sender = args.sender
        self.__region = args.region

        for recipient in args.recipients:
            self.__recipients.append(recipient)

        self.__client = boto3.client('ses', region_name=self.__region, aws_access_key_id=self.__key_id,
                                     aws_secret_access_key=self.__secret)

    def send(self, subject, message):
        self.__logger.info('Sending message:\n Subject: ' + subject + '\n body: ' + message)
        for recipient in self.__recipients:
            try:
                self.__client.send_email(
                    Destination={
                        'ToAddresses': [recipient],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': 'UTF-8',
                                'Data': message,
                            },
                        },
                        'Subject': {
                            'Charset': 'UTF-8',
                            'Data': subject,
                        },
                    },
                    Source=self.__sender
                )
            # Display an error if something goes wrong.
            except ClientError as e:
                self.__logger.error('Failed to send email to ' + recipient)
                self.__logger.debug(e.response['Error']['Message'])
