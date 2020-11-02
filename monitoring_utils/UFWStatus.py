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

import subprocess
import sys


class UFWStatus:

    def __init__(self, status, warn_inactive, logging, loggingpolicy, incoming, outgoing, routing, rules):
        self.__warn_inactive = warn_inactive
        self.__rules = self.parse_rules(rules)
        self.__routing = routing
        self.__outgoing = outgoing
        self.__incoming = incoming
        self.__loggingpolicy = loggingpolicy
        self.__logging = logging
        self.__status = status
        self.__running_config = self.get_running_config()

    def main(self):

        self.check_status()
        self.check_defaults()
        self.check_rules()
        self.check_non_critical()

        print("OK")
        sys.exit(0)

    def check_status(self):
        for running_config in self.__running_config:
            if 'status' == running_config[0]:
                if self.__status != running_config[1]:
                    print('CRITICAL: Firewall status does not match. Expected ' \
                          + self.__status + ' got ' + running_config[1])
                    sys.exit(2)
                elif 'inactive' == self.__status:
                    if 'on' == self.__warn_inactive:
                        print("WARNING: UFW inactive")
                        sys.exit(1)

                    print("OK: UFW inactive")
                    sys.exit(0)
                return

    def check_non_critical(self):

        for running_config in self.__running_config:
            if 'logging' == running_config[0]:
                if self.__logging != running_config[1]:
                    print('WARNING: Logging policy does not match. Expected ' \
                          + self.__logging + ' got ' + running_config[1])
                    sys.exit(1)

            elif 'loggingpolicy' == running_config[0]:
                if self.__loggingpolicy != running_config[1]:
                    print('WARNING: Logging policy does not match. Expected ' \
                          + self.__loggingpolicy + ' got ' + running_config[1])
                    sys.exit(1)

    def check_rules(self):
        # check if for each existing rule exists a configured rule
        for running_rule in self.__running_config:
            if 'rule' == running_rule[0]:
                found_rule = False
                for configured_rule in self.__rules:
                    if configured_rule[0] == running_rule[1] \
                            and configured_rule[1] == running_rule[3] \
                            and configured_rule[2] == running_rule[2]:
                        found_rule = True
                        break
                if False is found_rule:
                    print('CRITICAL: There is a configured rule on your system, which is not expected. From: ' \
                          + running_rule[1] + ' To: ' + running_rule[3] + ' Policy: ' + running_rule[2])
                    sys.exit(2)

        # check for each configured rule exist a rule on the system
        for configured_rule in self.__rules:
            found_rule = False
            for running_rule in self.__running_config:
                if 'rule' == running_rule[0]:
                    if configured_rule[0] == running_rule[1] \
                            and configured_rule[1] == running_rule[3] \
                            and configured_rule[2] == running_rule[2]:
                        found_rule = True
                        break

            if False is found_rule:
                print('CRITICAL: There is a rule configured, which is not on your system. From: ' + \
                      configured_rule[2] + ' To: ' + configured_rule[0] + ' Policy: ' + configured_rule[1])
                sys.exit(2)

    def check_defaults(self):
        for c in self.__running_config:
            if 'incoming' == c[0]:
                if self.__incoming != c[1]:
                    print('CRITICAL: Default incoming policy does not match. Expected ' \
                          + self.__incoming + ' got ' + c[1])
                    sys.exit(2)

            elif 'outgoing' == c[0]:
                if self.__outgoing != c[1]:
                    print('CRITICAL: Default outgoing policy does not match. Expected ' \
                          + self.__outgoing + ' got ' + c[1])
                    sys.exit(2)

            elif 'routing' == c[0]:
                if self.__routing != c[1]:
                    print('CRITICAL: Default routing policy does not match. Expected ' \
                          + self.__routing + ' got ' + c[1])
                    sys.exit(2)

    def get_running_config(self):
        out = subprocess.Popen(['sudo', 'ufw', 'status', 'verbose'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, stderr = out.communicate()

        if 0 != out.returncode:
            stderr = stderr.decode("utf-8")
            if 'a password is required' in stderr:
                print('UNKNOWN: can\'t run sudo without password. Please give executable'
                      ' rights without password in /ets/sudoers for \'ufw status verbose\' command.')
            elif 'command not found' in stderr:
                print('UNKNOWN: can\'t run ufw: command not found.')
            else:
                print('UNKNOWN: ' + stderr)

            sys.exit(3)
        stdout = stdout.decode("utf-8")

        parsed_config = []
        line_counter = 0
        parse_rules = False
        for line in stdout.split("\n"):
            if 0 == line_counter:
                parsed_config.append(('status', line.split()[1]))
            elif 1 == line_counter:
                parsed_config.append(('logging', line.split()[1]))
                parsed_config.append(('loggingpolicy', line.split()[2].replace('(', '').replace(')', '')))
            elif 2 == line_counter:
                policies = line.split(': ')[1].split(', ')
                parsed_config.append(('incoming', policies[0].split()[0]))
                parsed_config.append(('outgoing', policies[1].split()[0]))
                parsed_config.append(('routing', policies[2].split()[0]))
            elif '--' in line and not parse_rules:
                parse_rules = True
            elif parse_rules and '' != line:
                line = line.lower()

                if 'allow' in line:
                    parsed_config.append(self.parse_rule(line, 'allow'))
                elif 'deny' in line:
                    parsed_config.append(self.parse_rule(line, 'deny'))

                elif 'limit' in line:
                    parsed_config.append(self.parse_rule(line, 'limit'))

                elif 'reject' in line:
                    parsed_config.append(self.parse_rule(line, 'reject'))

                else:
                    print("UNKNOWN: Could not parse policy. Only action allow|deny|limit|reject [in|out|fwd] "
                          "are supported. Found policy " + line)

                    sys.exit(3)

            line_counter += 1

        return parsed_config

    def parse_rule(self, line, policy):
        policy_array = line.split(policy)
        rule_to = policy_array[0].strip().replace(' ', '-')
        policy_array = [e for e in policy_array[1].split('  ') if '' != e]
        rule_policy = (policy + policy_array[0]).strip().replace(' ', '-')
        rule_from = policy_array[1].strip().replace(' ', '-')

        return tuple(('rule', rule_from, rule_policy, rule_to))

    def parse_rules(self, rules):
        parsed_rules = []
        for rule in rules:
            parsed_rule = rule.lower().split(',')
            if 3 != len(parsed_rule):
                print('UNKNOWN: Rule does not match expected format. Got' + rule)
                sys.exit(3)
            parsed_rules.append(parsed_rule)

        return parsed_rules
