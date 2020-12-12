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


class NmapScriptExecutor:

    def __init__(self, logger, status_builder):
        self.__logger = logger
        self.__status_builder = status_builder
        self.__scripts = {}

    def add_script(self, script_name, script):
        self.__scripts[script_name] = script

    def execute(self, report, ignore_port):
        self.__logger.info('Checking report')

        for script_name in self.__scripts:
            self.__logger.info('Checking Execute script "{script_name}"'.format(script_name=script_name))
            host_port_maps = report.get_hosts_with_script(script_name)
            for host_port_map in host_port_maps:
                host_port_map['ips'] = []
                for address in host_port_map['host'].get_addresses():
                    if address.is_ip():
                        host_port_map['ips'].append(address.get_addr())
                        for port in host_port_map['ports']:
                            if port.get_port() in ignore_port.get(address.get_addr(), []):
                                host_port_map['ports'].remove(port)
                                self.__logger.debug('Ignoring port "{port}" with executed script "{script_name}"'
                                                    .format(port=port.get_port(), script_name=script_name))

                if 0 == len(host_port_map['ports']):
                    self.__logger.debug(
                        'Ignoring Host with ips "{ips}" because no port with executed script "{script_name}"'
                            .format(ips='", "'.join(host_port_map['ips']), script_name=script_name)
                    )
                    host_port_maps.remove(host_port_map)

                ports_executed = []
                for ip in host_port_map['ips']:
                    executor_host_configs = self.__scripts[script_name].get_config_for_host(ip)
                    if None == executor_host_configs:
                        self.__logger.debug('No config for ip "{ip}" in script "{script_name}" set'
                                            .format(ip=ip, script_name=script_name)
                                            )
                        continue

                    for executor_host_config_port in executor_host_configs:
                        port_config = executor_host_configs[executor_host_config_port]
                        executed = False
                        for port in host_port_map['ports']:
                            if executor_host_config_port == port.get_port():
                                self.__logger.info(
                                    'Execute script "{script_name}" on Port "{port}" from host wit ip "{ip}"'
                                        .format(ip=ip, script_name=script_name, port=port.get_port())
                                )
                                self.__scripts[script_name].execute(port, port.get_script(script_name), port_config)
                                ports_executed.append(port)
                                executed = True
                                break
                        if not executed:
                            self.__status_builder.unknown(
                                'Script "{script_name}" has a configuration for Port "{port}" at host wit ip "{ip}" '
                                'but the script was not executed on this port.'
                                    .format(ip=ip, script_name=script_name, port=executor_host_config_port)
                            )

                for port in host_port_map['ports']:
                    if port not in ports_executed:
                        self.__status_builder.critical(
                            'Script "{script_name}" has no configuration for Port "{port}" at host wit ips "{ip}" but '
                            'the script was executed on this port. Either setup a configuration or ignore this port.'
                                .format(ip='", "'.join(host_port_map['ips']), script_name=script_name,
                                        port=port.get_port())
                        )
