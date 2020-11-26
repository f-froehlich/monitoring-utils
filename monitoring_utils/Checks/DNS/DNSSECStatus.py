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


from datetime import datetime

from monitoring_utils.Core.Executor.DNSExecutor import DNSExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class DNSSECStatus(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__warning_days = None
        self.__critical_days = None
        self.__domains = None
        self.__resolver = None
        self.__ignoreroot = None
        self.__ignoretld = None
        self.__expire_dates = {}
        self.__executor = None

        Plugin.__init__(self, 'Check DNSSEC status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-w', '--warning', dest='warning', default=10, type=int,
                                   help='Days left to exit in warning state')
        self.__parser.add_argument('-c', '--critical', dest='critical', default=5, type=int,
                                   help='Days left to exit in critical state')
        self.__parser.add_argument('-d', '--domain', dest='domains', action='append',
                                   help='Domains to check', default=[])
        self.__parser.add_argument('-r', '--resolver', dest='resolver', default='1.1.1.1',
                                   help='Resolver for DNS Queries')
        self.__parser.add_argument('--ignore-root', dest='ignoreroot', action='store_true',
                                   help='Ignore the root zone "."')
        self.__parser.add_argument('--ignore-tld', dest='ignoretld', action='store_true',
                                   help='Ignore the tld zones e.g. ".eu" or ".com" and also the root zone "."')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__warning_days = args.warning
        self.__critical_days = args.critical
        self.__domains = args.domains
        self.__resolver = args.resolver
        self.__ignoreroot = args.ignoreroot
        self.__ignoretld = args.ignoretld
        self.__executor = DNSExecutor(self.__logger, self.__parser, self.__status_builder, self.__resolver)

    def run(self):

        self.compute_expire_dates()
        self.compute_state()

        self.__status_builder.exit(all_outputs=True)

    def compute_expire_dates(self):
        for domain in self.__domains:
            # search from root zone to domain
            zones = domain.split('.')
            zones.append('.')
            zones.reverse()

            last_zone = None
            for zone in zones:
                current_zone = zone if None == last_zone else zone + '.' + last_zone if '.' != last_zone else zone + '.'

                if None == last_zone and (self.__ignoreroot or self.__ignoretld):
                    # ignore root zone and TLD if set.
                    self.__logger.info('Ignore root zone "."')
                    last_zone = current_zone
                    continue
                if '.' == last_zone and self.__ignoretld:
                    # ignore TLD if set
                    self.__logger.info('Ignore tld zone "' + current_zone + '"')
                    last_zone = current_zone
                    continue

                expire_date = self.__expire_dates.get(current_zone, None)
                if None == expire_date:
                    # domain not handled yet
                    self.__logger.info('Check expiration of zone "' + current_zone + '"')
                    rrsigs = self.__executor.resolve_RRSIG(current_zone)
                    if None == rrsigs or 0 == len(rrsigs):
                        # domain not signed or no RRSIG exist
                        last_zone = current_zone
                        self.__expire_dates[current_zone] = '-'
                        continue

                    for rrsig in rrsigs:
                        # get expiration and signing date of domain
                        rrsig_array = rrsig.to_text().split()
                        date = int(rrsig_array[4])
                        signing_date = int(rrsig_array[5])
                        self.__logger.debug('Expiration date of zone "' + current_zone + '" is "' + str(date) + '"')
                        self.__logger.debug(
                            'Signing date of zone "' + current_zone + '" is "' + str(signing_date) + '"')

                        # get expiration and signing date of parent
                        signing_date_parent = self.__expire_dates.get(last_zone, (None, None))[0]
                        expire_date_parent = self.__expire_dates.get(last_zone, (None, None))[1]
                        self.__logger.debug('Expiration date of parent zone "' + last_zone + '" is "' +
                                            str(signing_date_parent) + '"')
                        self.__logger.debug(
                            'Signing date of parent zone "' + last_zone + '" is "' + str(expire_date_parent) + '"')

                        if '-' == expire_date_parent:
                            # parent zone is not signed -> child zone can't be signed
                            self.__expire_dates[current_zone] = ('-', '-')

                        elif None == expire_date_parent:
                            # No expiration date for parent zone found -> it is the root zone, TLD or first valid domain
                            expire_date = self.__expire_dates.get(current_zone, (None, None))[1]
                            if None == expire_date:
                                # domain has no expire date yet -> first RRSIG
                                self.__logger.debug('Set expiration date of zone "' + current_zone + '" to "' +
                                                    str(date) + '"')
                                self.__expire_dates[current_zone] = (signing_date, date)

                            elif date > expire_date:
                                # domain has an expire date but also found an RRSIG with grater live time
                                # -> caused mostly during key rollover
                                self.__logger.debug(
                                    'Update expiration date of zone "' + current_zone + '" from "' + str(expire_date)
                                    + '"to "' + str(date) + '"')
                                self.__expire_dates[current_zone] = (signing_date, date)
                        else:
                            # parent hase an expiration date
                            expire_date = self.__expire_dates.get(current_zone, (None, None))[1]
                            if None == expire_date:
                                # domain has no expire date yet -> first RRSIG
                                if date < expire_date_parent:
                                    # expire date of current domain is lower than from the parent zone
                                    # -> set expire date from domain
                                    self.__logger.debug('Set expiration date of zone "' + current_zone + '" to "' +
                                                        str(date) + '"')
                                    self.__expire_dates[current_zone] = (signing_date, date)
                                else:
                                    # expire date of parent zone is lower than from current domain
                                    # -> set expire date from parent
                                    self.__logger.debug('Set expiration date of zone "' + current_zone + '" to "' +
                                                        str(expire_date_parent) + '"')
                                    self.__expire_dates[current_zone] = (signing_date_parent, expire_date_parent)

                            elif date > expire_date and date < expire_date_parent:
                                # expire date from current RRSIG is greater than the expire date from previous domain
                                # and lower than from parent zone -> set current expiration date.
                                # -> caused mostly during key rollover
                                self.__logger.debug(
                                    'Update expiration date of zone "' + current_zone + '" from "' + str(expire_date)
                                    + '" to "' + str(date) + '"')
                                self.__expire_dates[current_zone] = (signing_date, date)

                last_zone = current_zone

    def compute_state(self):
        now = datetime.now()
        current = int(now.strftime("%Y%m%d%H%M%S"))
        warning_sec = self.__warning_days * 86400  # * 60 * 60 * 24
        critical_sec = self.__critical_days * 86400  # * 60 * 60 * 24

        for domain, dates in self.__expire_dates.items():

            if '-' == dates:
                # zone is not signed -> unknown message already send
                continue

            signing_date = dates[0]
            expire_date = dates[1]

            # format timestamps
            expire_timestamp = datetime.strptime(str(expire_date), "%Y%m%d%H%M%S").timestamp()
            expire_pretty = datetime.fromtimestamp(expire_timestamp).strftime("%Y-%m-%d %H:%M:%S")
            signing_timestamp = datetime.strptime(str(signing_date), "%Y%m%d%H%M%S").timestamp()
            current_timestamp = datetime.strptime(str(current), "%Y%m%d%H%M%S").timestamp()

            # remaining time
            rem_time = expire_timestamp - current_timestamp
            rem_days = round(rem_time / 86400, 2)  # / 60 / 60 / 24

            # elapsed time
            elapsed_time = current_timestamp - signing_timestamp

            # complete time
            complete_time = elapsed_time + rem_time

            # calculate percentage
            percentage = max(0, min(100, round((1 - elapsed_time / complete_time) * 100, 2)))
            w_percentage = max(0, min(100, round((warning_sec / complete_time) * 100, 2)))
            c_percentage = max(0, min(100, round((critical_sec / complete_time) * 100, 2)))

            # create perfdata
            perfdata = domain + '=' + str(percentage) + '%;' + str(w_percentage) + '%;' + str(c_percentage) + '%;'

            if current > expire_date:
                # domain expired
                metadata = '0% / 0 days remaining (expired at ' + expire_pretty + ')'
                self.__status_builder.critical('Zone "' + domain + '" is expired;' + metadata + ';|' + perfdata)
                self.__logger.info('Zone "' + domain + '" is expired')

                continue

            metadata = str(percentage) + '% / ' + str(rem_days) + ' days remaining (expire at ' + expire_pretty + ')'
            if self.__critical_days > rem_days:
                # critical
                self.__status_builder.critical('Zone "' + domain + '" is very short before expiration;' + metadata +
                                               ';|' + perfdata)
                self.__logger.info('Zone "' + domain + '" is very short before expiration')
            elif self.__warning_days > rem_days:
                # warning
                self.__status_builder.warning('Zone "' + domain + '" is short before expiration;' + metadata
                                              + ';|' + perfdata)
                self.__logger.info('Zone "' + domain + '" is short before expiration')
            else:
                # valid
                self.__status_builder.success('Zone "' + domain + '" is valid;' + metadata + ';|' + perfdata)
                self.__logger.info('Zone "' + domain + '" is valid')
