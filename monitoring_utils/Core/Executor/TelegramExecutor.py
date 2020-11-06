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

import telegram


class TelegramExecutor:

    def __init__(self, parser, logger, status_builder, token=None, chat_ids=[], groups=[]):
        self.__status_builder = status_builder
        self.__logger = logger
        self.__parser = parser
        self.__chat_ids = chat_ids
        self.__groups = groups
        self.__token = token
        self.__bot = None if None is token else telegram.Bot(token=self.__token)

    def add_args(self):
        self.__parser.add_argument('-T', '--token', dest='token', type=str, help='Token of telegram bot', required=True)
        self.__parser.add_argument('-U', '--user', dest='users', action='append', default=[], help='Chat id of user')
        self.__parser.add_argument('-G', '--group', dest='groups', action='append', default=[],
                                   help='Chat id of group, dont place "-" before id')

    def configure(self, args):
        self.__token = args.token
        for id in args.users:
            try:
                self.__chat_ids.append(int(id))
            except Exception:
                self.__status_builder.critical('Can\'t parse "' + id + '" to int')
                self.__status_builder.exit()
        for id in args.groups:
            try:
                self.__groups.append(-1 * int(id))
            except Exception:
                self.__status_builder.critical('Can\'t parse "' + id + '" to int')
                self.__status_builder.exit()

        self.__bot = telegram.Bot(token=self.__token)

    def send(self, message):
        self.__logger.info('Sending message:\n' + message)
        for chat_id in self.__chat_ids:
            self.send_message_to_chat(message, chat_id)
        for chat_id in self.__groups:
            self.send_message_to_chat(message, chat_id)

    def send_message_to_chat(self, message, chat):
        chat_to = 'user' if chat > 0 else 'group'
        try:
            self.__logger.debug('Sending message to ' + chat_to + ' with id "' + str(chat) + '"')
            self.__bot.sendMessage(chat_id=chat, text=message)
        except telegram.TelegramError:
            self.__logger.debug('Can\'t send message to ' + chat_to + ' with id "' + str(chat) + '"')
            self.__status_builder.critical('Can\'t send message to ' + chat_to + ' with id "' + str(chat) + '"')

    def get_updates(self):

        return self.__bot.get_updates()
