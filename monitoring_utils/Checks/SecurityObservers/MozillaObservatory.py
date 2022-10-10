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
import json
import time
from copy import copy

from monitoring_utils.Core.Executor.WebExecutor import WebExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class MozillaObservatory(Plugin):

    def __init__(self):
        self.__criticalgrade = None
        self.__criticalscore = None
        self.__warninggrade = None
        self.__warningscore = None
        self.__args = None
        self.__host = None
        self.__ignorehidden = None
        self.__ignorerescan = None
        self.__web_executor = None
        self.__scan_test_config = {}

        Plugin.__init__(self, 'Check mozilla http-observatory for a host')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__web_executor = WebExecutor(self.get_logger(), self.__parser, self.get_status_builder())
        self.__web_executor.add_args()

        # override parameters for web executor
        self.__parser.add_argument('-u', '--uri', dest='uri', type=str,
                                   help='Endpoint URI of http observatory. Default: /api/v1', default='/api/v1')
        self.__parser.add_argument('-d', '--domain', dest='domain', type=str,
                                   help='Endpoint domain of http observatory. Default: http-observatory.security.mozilla.org',
                                   default='http-observatory.security.mozilla.org')
        self.__parser.add_argument('-p', '--port', dest='port', type=int, help='Endpoint port of http observatory')

        # set own parameter

        self.__parser.add_argument('-iH', '--ignore-hidden', dest='ignorehidden', required=False,
                                   action='store_true', default=False,
                                   help='If set the scan result will not be hidden from public scan results')

        self.__parser.add_argument('-iR', '--ignore-rescan', dest='ignorerescan', required=False,
                                   action='store_true', default=False, help='If set we don\'t force to rescan the site')

        self.__parser.add_argument('-w', '--warning', dest='warningscore', required=False, default=90,
                                   type=int, help='Bound to exit in WARNING state. Default: 90')
        self.__parser.add_argument('-W', '--warning-grade', dest='warninggrade', required=False, default='B',
                                   help='Grade to exit in WARNING state. Default: B',
                                   choices=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E+',
                                            'E', 'E-', 'F+', 'F', 'F-'])

        self.__parser.add_argument('-c', '--critical', dest='criticalscore', required=False, default=75,
                                   type=int, help='Bound to exit in CRITICAL state. Default: 75')
        self.__parser.add_argument('-C', '--critical-grade', dest='criticalgrade', required=False, default='C',
                                   help='Grade to exit in CRITICAL state. Default: C',
                                   choices=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E+',
                                            'E', 'E-', 'F+', 'F', 'F-'])

        self.__parser.add_argument('--config', dest='testconfig', action='append', default=[],
                                   help='Config for each individual test. Format: NAME:WARNING_SCORE:CRITICAL_SCORE. To skip a test define NAME:-:-')

        self.__parser.add_argument('-H', '--host', dest='host', required=True, help='Host to scan')

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__args = args

        config_error = False

        if args.warningscore <= args.criticalscore:
            config_error = True
            self.__status_builder.unknown("Warning score must be grater than critical score")
        if self.map_grade(args.warninggrade) >= self.map_grade(args.criticalgrade):
            config_error = True
            self.__status_builder.unknown("Warning grade must be better than critical grade")

        self.__host = args.host
        self.__ignorehidden = args.ignorehidden
        self.__ignorerescan = args.ignorerescan
        self.__warningscore = args.warningscore
        self.__warninggrade = args.warninggrade
        self.__criticalscore = args.criticalscore
        self.__criticalgrade = args.criticalgrade

        for testconfig in args.testconfig:
            config = testconfig.split(':')
            if len(config) != 3:
                config_error = True
                self.__status_builder.unknown(f"Config has an invalid format: {testconfig}")
                continue

            try:
                warning = -1 if '-' == config[1] else int(config[1])
            except Exception:
                warning = 0
                config_error = True
                self.__status_builder.unknown(
                    f"Config has an invalid format: {testconfig}. Required int or - as warning score")

            try:
                critical = -10 if '-' == config[2] else int(config[2])
            except Exception:
                critical = 0
                config_error = True
                self.__status_builder.unknown(
                    f"Config has an invalid format: {testconfig}. Required int or - as critical score")

            if warning <= critical:
                config_error = True
                self.__status_builder.unknown(
                    f"Config has an invalid format: {testconfig}. Required warning score better than critical score")

            self.__scan_test_config[config[0]] = {
                'ignore': True if (config[1] == config[2] == '-') else False,
                'warning': warning,
                'critical': critical
            }

        if config_error:
            self.__status_builder.exit()

    def run(self):
        scan = self.scan_host(self.__host, not self.__ignorerescan, not self.__ignorehidden)
        scan_tests = self.get_scan_tests(scan)
        self.check_scan(scan)
        self.check_scan_tests(scan_tests)

        self.__status_builder.success('All checks passed.')

    def map_grade(self, grade):
        return {
            'A+': 1,
            'A': 2,
            'A-': 3,
            'B+': 4,
            'B': 5,
            'B-': 6,
            'C+': 7,
            'C': 8,
            'C-': 9,
            'D+': 10,
            'D': 11,
            'D-': 12,
            'E+': 13,
            'E': 14,
            'E-': 15,
            'F+': 16,
            'F': 17,
            'F-': 18,
        }.get(grade, None)

    def reverse_map_grade(self, grade):
        return {
            1: 'A+',
            2: 'A',
            3: 'A-',
            4: 'B+',
            5: 'B',
            6: 'B-',
            7: 'C+',
            8: 'C',
            9: 'C-',
            10: 'D+',
            11: 'D',
            12: 'D-',
            13: 'E+',
            14: 'E',
            15: 'E-',
            16: 'F+',
            17: 'F',
            18: 'F-',
        }.get(grade, None)

    def __get_scan_test_config(self, name):

        return self.__scan_test_config.get(name, {
            'ignore': False,
            'warning': -1,
            'critical': -10
        })

    def check_scan_tests(self, scan_tests):
        for test in scan_tests:
            config = self.__get_scan_test_config(test.get_name())
            if config['ignore']:
                self.__logger.info(
                    f"Ignoring test {test.get_name()} {'but tests passed' if test.is_passed() else 'and test failed'}")
                continue
            if test.get_score_modifier() <= config['critical']:
                self.__status_builder.critical(
                    f"""Test {test.get_name()} failed. Score modifier is {test.get_score_modifier()}. 
Expected: {test.get_expectation()}
Result: {test.get_result()}
Description: {test.get_score_description()}
See Details on: https://infosec.mozilla.org/guidelines/web_security#{test.get_name()}
""".replace("\n", " "))
            elif test.get_score_modifier() <= config['warning']:
                self.__status_builder.warning(
                    f"""Test {test.get_name()} failed. Score modifier is {test.get_score_modifier()}. 
Expected: {test.get_expectation()}
Result: {test.get_result()}
Description: {test.get_score_description()}
See Details on: https://infosec.mozilla.org/guidelines/web_security#{test.get_name()}
""".replace("\n", " "))

    def check_scan(self, scan):
        if scan.get_score() <= self.__criticalscore:
            self.__logger.info(
                f'Score of scan is lower than critical score. Expected higher than {self.__criticalscore} got {scan.get_score()}')
            self.__status_builder.critical(
                f'Score of scan is lower than critical score. Expected higher than {self.__criticalscore} got {scan.get_score()}')
        elif self.map_grade(scan.get_grade()) >= self.map_grade(self.__criticalgrade):
            self.__logger.info(
                f'Grade of scan is lower than critical grade. Expected higher than {self.__criticalgrade} got {scan.get_grade()}')
            self.__status_builder.critical(
                f'Grade of scan is lower than critical grade. Expected higher than {self.__criticalgrade} got {scan.get_grade()}')
        elif scan.get_score() >= self.__warningscore:
            self.__logger.info(
                f'Score of scan is lower than warning score. Expected higher than {self.__warningscore} got {scan.get_score()}')
            self.__status_builder.warning(
                f'Score of scan is lower than warning score. Expected higher than {self.__warningscore} got {scan.get_score()}')
        elif self.map_grade(scan.get_grade()) <= self.map_grade(self.__warninggrade):
            self.__logger.info(
                f'Grade of scan is lower than warning grade. Expected higher than {self.__warninggrade} got {scan.get_grade()}')
            self.__status_builder.warning(
                f'Grade of scan is lower than warning grade. Expected higher than {self.__warninggrade} got {scan.get_grade()}')

    def get_scan_tests(self, scan):
        self.__logger.debug(f'Get scan results for scan {scan.get_scan_id()}')

        executor = WebExecutor(self.__logger, self.__parser, self.__status_builder)
        args = copy(self.__args)
        args.uri = f'{args.uri}/getScanResults?scan={scan.get_scan_id()}'
        executor.configure(args)

        result = json.loads(executor.run_get())
        self.__logger.debug(result)
        tests = []
        for test_data in result.values():
            test = Test(test_data)
            scan.add_test(test)
            tests.append(test)

        return tests

    def scan_host(self, host, force_rescan=True, hide_results=True):
        self.__logger.debug(f'Scanning host {host} with rescan={force_rescan}, hide_results={hide_results}')
        executor = WebExecutor(self.__logger, self.__parser, self.__status_builder)
        args = copy(self.__args)
        args.uri = f'{args.uri}/analyze?host={self.__host}'
        executor.configure(args)

        while True:
            result = json.loads(
                executor.run_post(data={'rescan': not self.__ignorerescan, 'hidden': not self.__ignorehidden})
            )
            self.__logger.debug(result)

            if None is not result.get('error', None):
                self.__logger.error(f'Scan for host {host} is failed')
                self.__status_builder.critical(result.get('text', result['error']))
                self.__status_builder.exit()

            scan = Scan(result)

            if scan.is_finished():
                self.__logger.debug(f'Scan for host {host} is finished')
                break
            elif scan.is_failed():
                self.__logger.error(f'Scan for host {host} is failed')
                self.__status_builder.unknown(f'Scan for host {host} is failed')
                self.__status_builder.exit()

            else:
                self.__logger.debug('Wait until scan finished')
                time.sleep(10)

        return scan


class Scan:

    def __init__(self, scan):
        self.__end_time = scan['end_time']
        self.__grade = scan['grade']
        self.__hidden = scan['hidden']
        self.__response_headers = scan['response_headers']
        self.__scan_id = scan['scan_id']
        self.__score = scan['score']
        self.__likelihood_indicator = scan['likelihood_indicator']
        self.__start_time = scan['start_time']
        self.__state = scan['state']
        self.__tests_failed = scan['tests_failed']
        self.__tests_passed = scan['tests_passed']
        self.__tests_quantity = scan['tests_quantity']
        self.__tests = []

    def get_tests(self):
        return self.__tests

    def add_test(self, test):
        self.__tests.append(test)

    def get_end_time(self):
        return self.__end_time

    def get_grade(self):
        return self.__grade

    def get_hidden(self):
        return self.__hidden

    def get_response_headers(self):
        return self.__response_headers

    def get_scan_id(self):
        return self.__scan_id

    def get_score(self):
        return self.__score

    def get_likelihood_indicator(self):
        return self.__likelihood_indicator

    def get_start_time(self):
        return self.__start_time

    def get_state(self):
        return self.__state

    def get_tests_failed(self):
        return self.__tests_failed

    def get_tests_passed(self):
        return self.__tests_passed

    def get_tests_quantity(self):
        return self.__tests_quantity

    def is_aborted(self):
        return 'ABORTED' == self.__state

    def is_failed(self):
        return 'FAILED' == self.__state

    def is_finished(self):
        return 'FINISHED' == self.__state

    def is_pending(self):
        return 'PENDING' == self.__state

    def is_running(self):
        return 'RUNNING' == self.__state


class Test:

    def __init__(self, data):
        self.__expectation = data['expectation']
        self.__name = data['name']
        self.__output = data['output']  # todo different for each test
        self.__pass = data['pass']
        self.__result = data['result']
        self.__score_description = data['score_description']
        self.__score_modifier = data['score_modifier']

    def get_expectation(self):
        return self.__expectation

    def get_name(self):
        return self.__name

    def get_output(self):
        return self.__output

    def is_passed(self):
        return self.__pass

    def get_result(self):
        return self.__result

    def get_score_description(self):
        return self.__score_description

    def get_score_modifier(self):
        return self.__score_modifier
