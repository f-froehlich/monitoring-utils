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


from monitoring_utils.Core.Executor.CLIExecutor import CLIExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class UFWStatus(Plugin):

    def __init__(self):
        self.__warn_inactive = None
        self.__rules = None
        self.__routing = None
        self.__outgoing = None
        self.__incoming = None
        self.__loggingpolicy = None
        self.__logging = None
        self.__status = None
        self.__running_config = None

        Plugin.__init__(self, 'Check ufw status and rules')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__parser.add_argument('-s', '--status', dest='status', default='active',
                                   help='Status of ufw')
        self.__parser.add_argument('--warn-inactive', dest='warninactive', default='on',
                                   help='Warn on inactive UFW')
        self.__parser.add_argument('-l', '--logging', dest='logging', default='on',
                                   help='Status of logging')
        self.__parser.add_argument('-L', '--logging-policy', dest='loggingpolicy',
                                   default='low', help='Status of logging level')
        self.__parser.add_argument('-I', '--in', dest='incoming', default='deny',
                                   help='Default incoming policy')
        self.__parser.add_argument('-O', '--out', dest='outgoing',
                                   default='allow', help='Default outgoing policy')
        self.__parser.add_argument('-R', '--routing', dest='routing',
                                   default='disabled', help='Default routing policy')
        self.__parser.add_argument('-r', '--rule', dest='rule', action='append',
                                   help='Firewall rule from,to,action', default=[])

    def configure(self, args):
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()

        self.__status = args.status
        self.__warn_inactive = args.warninactive
        self.__logging = args.logging
        self.__loggingpolicy = args.loggingpolicy
        self.__incoming = args.incoming
        self.__outgoing = args.outgoing
        self.__routing = args.routing
        self.__rules = self.parse_rules(args.rule)

        self.__running_config = self.get_running_config()

    def run(self):

        self.check_status()
        self.check_defaults()
        self.check_rules()

        self.__status_builder.success('All checks passed.')

    def check_status(self):
        self.__logger.debug('Check status')
        for running_config in self.__running_config:
            if 'status' == running_config[0]:
                if self.__status != running_config[1]:
                    self.__logger.info('Firewall status not match')
                    self.__status_builder.critical('Firewall status does not match. Expected '
                                                   + self.__status + ' got ' + running_config[1])
                    self.__status_builder.exit()
                elif 'inactive' == self.__status:
                    self.__logger.info('Firewall inactive')
                    if 'on' == self.__warn_inactive:
                        self.__logger.debug('Send warning because firewall is inactive')
                        self.__status_builder.warning("UFW inactive")
                        self.__status_builder.exit()

                    self.__logger.debug('Firewall inactive and should, don\'t send warning')
                    self.__status_builder.success("UFW inactive and should")
                    self.__status_builder.exit()

            elif 'logging' == running_config[0]:
                self.__logger.debug('Check logging')
                if self.__logging != running_config[1]:
                    self.__status_builder.warning('Logging policy does not match. Expected '
                                                  + self.__logging + ' got ' + running_config[1])

            elif 'loggingpolicy' == running_config[0]:
                self.__logger.debug('Check logging policy')
                if self.__loggingpolicy != running_config[1]:
                    self.__status_builder.warning('Logging policy does not match. Expected '
                                                  + self.__loggingpolicy + ' got ' + running_config[1])

    def check_rules(self):
        # check if for each existing rule exists a configured rule
        self.__logger.info('Check if for each existing rule exists a configured rule')
        for running_rule in self.__running_config:
            if 'rule' == running_rule[0]:
                self.__logger.debug('Check rule From "' + running_rule[1] + '" to "' + running_rule[2] + '" policy "'
                                    + running_rule[3] + '"')
                found_rule = False
                for configured_rule in self.__rules:
                    if configured_rule[0] == running_rule[1] \
                            and configured_rule[1] == running_rule[3] \
                            and configured_rule[2] == running_rule[2]:
                        self.__logger.debug('Found rule')
                        found_rule = True
                        break
                if False is found_rule:
                    self.__logger.debug('No matching rule found')
                    self.__status_builder.critical('There is a configured rule on your system, which is not expected.' +
                                                   ' From: ' + running_rule[1] + ' To: ' + running_rule[3] +
                                                   ' Policy: ' + running_rule[2])

        # check for each configured rule exist a rule on the system
        self.__logger.info('check for each configured rule exist a rule on the system')
        for configured_rule in self.__rules:
            found_rule = False
            self.__logger.debug('Check rule From "' + configured_rule[0] + '" to "' + configured_rule[2] + '" policy "'
                                + configured_rule[1] + '"')
            for running_rule in self.__running_config:
                if 'rule' == running_rule[0]:
                    if configured_rule[0] == running_rule[1] \
                            and configured_rule[1] == running_rule[3] \
                            and configured_rule[2] == running_rule[2]:
                        self.__logger.debug('Found rule')
                        found_rule = True
                        break

            if False is found_rule:
                self.__logger.debug('No matching rule found')
                self.__status_builder.critical('There is a rule configured, which is not on your system. From: ' +
                                               configured_rule[0] + ' To: ' + configured_rule[1] + ' Policy: ' +
                                               configured_rule[2])

    def check_defaults(self):
        self.__logger.info('Checking default policies')
        for c in self.__running_config:
            if 'incoming' == c[0]:
                self.__logger.debug('Check incoming policy')
                if self.__incoming != c[1]:
                    self.__logger.debug('Incoming policy not match')
                    self.__status_builder.critical('Default incoming policy does not match. Expected '
                                                   + self.__incoming + ' got ' + c[1])
                else:
                    self.__logger.debug('Incoming policy match')

            elif 'outgoing' == c[0]:
                self.__logger.debug('Check outgoing policy')

                if self.__outgoing != c[1]:
                    self.__logger.debug('Outgoing policy not match')
                    self.__status_builder.critical('Default outgoing policy does not match. Expected '
                                                   + self.__outgoing + ' got ' + c[1])
                else:
                    self.__logger.debug('Outgoing policy match')

            elif 'routing' == c[0]:
                self.__logger.debug('Check routing policy')
                if self.__routing != c[1]:
                    self.__logger.debug('Routing policy not match')
                    self.__status_builder.critical('Default routing policy does not match. Expected '
                                                   + self.__routing + ' got ' + c[1])
                else:
                    self.__logger.debug('Routing policy match')

    def get_running_config(self):
        cli_executor = CLIExecutor(logger=self.__logger, status_builder=self.__status_builder,
                                   command_array=['sudo', 'ufw', 'status', 'verbose'])
        output = cli_executor.run()

        parsed_config = []
        line_counter = 0
        parse_rules = False
        for line in output:
            if '' == line:
                continue

            self.__logger.debug('Parse line "' + line + '"')

            if 0 == line_counter:
                self.__logger.debug('Add status "' + line.split()[1] + '"')
                parsed_config.append(('status', line.split()[1]))
            elif 1 == line_counter:
                self.__logger.debug('Add logging "' + line.split()[1] + '"')
                parsed_config.append(('logging', line.split()[1]))
                policy = line.split()[2].replace('(', '').replace(')', '')
                self.__logger.debug('Add logging policy "' + policy + '"')
                parsed_config.append(('loggingpolicy', policy))
            elif 2 == line_counter:
                policies = line.split(': ')[1].split(', ')
                policy_in = policies[0].split()[0]
                policy_out = policies[1].split()[0]
                policy_routing = policies[2].split()[0]
                self.__logger.debug('Add default rules in: "' + policy_in + '", out: "' + policy_out + '", routing: "'
                                    + policy_routing + '", ')
                parsed_config.append(('incoming', policy_in))
                parsed_config.append(('outgoing', policy_out))
                parsed_config.append(('routing', policy_routing))
            elif '--' in line and not parse_rules:
                self.__logger.debug('Begin parsing rules')
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
                    self.__logger.debug('Could not parse policy. "' + line + '"')
                    self.__status_builder.unknown(
                        "Could not parse policy. Only action allow|deny|limit|reject [in|out|fwd] "
                        "are supported. Found policy " + line)

                    self.__status_builder.exit()

            line_counter += 1

        return parsed_config

    def parse_rule(self, line, policy):

        policy_array = line.split(policy)
        rule_to = policy_array[0].strip().replace(' ', '-')
        policy_array = [e for e in policy_array[1].split('  ') if '' != e]
        rule_policy = (policy + policy_array[0]).strip().replace(' ', '-')
        rule_from = policy_array[1].strip().replace(' ', '-')

        self.__logger.debug('Add rule: From "' + rule_from + '", to "' + rule_to + '", policy "' + rule_policy + '"')

        return tuple(('rule', rule_from, rule_policy, rule_to))

    def parse_rules(self, rules):
        self.__logger.info('Parsing rules')

        parsed_rules = []
        for rule in rules:
            self.__logger.debug('Parse rule "' + rule + '"')
            parsed_rule = rule.lower().split(',')
            if 3 != len(parsed_rule):
                self.__logger.debug('Rule "' + rule + '" mismatch conditions. Must be in the Format "from,to,action"')
                self.__status_builder.unknown('Rule does not match expected format. Got' + rule)
                self.__status_builder.exit()

            parsed_rules.append(parsed_rule)

        return parsed_rules
