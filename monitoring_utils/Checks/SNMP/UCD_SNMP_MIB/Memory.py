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


from monitoring_utils.Core.Executor.SNMPExecutor import SNMPExecutor
from monitoring_utils.Core.Outputs.Output import Output
from monitoring_utils.Core.Outputs.Perfdata import Perfdata
from monitoring_utils.Core.Plugin.Plugin import Plugin


class Memory(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None

        self.__snmp_executor = None
        self.__memory_id = None
        self.__warning_total = None
        self.__critical_total = None
        self.__check_total = None
        self.__warning_swap = None
        self.__critical_swap = None
        self.__check_swap = None
        self.__warning_swap_txt = None
        self.__critical_swap_txt = None
        self.__check_swap_txt = None
        self.__warning_real = None
        self.__critical_real = None
        self.__check_real = None
        self.__warning_real_txt = None
        self.__critical_real_txt = None
        self.__check_real_txt = None
        self.__warning_shared = None
        self.__critical_shared = None
        self.__check_shared = None
        self.__warning_buffer = None
        self.__critical_buffer = None
        self.__check_buffer = None
        self.__warning_cache = None
        self.__critical_cache = None
        self.__check_cache = None
        self.__warning_min_swap = None
        self.__critical_min_swap = None
        self.__check_min_swap = None
        self.__oid = '1.3.6.1.4.1.2021.4'

        Plugin.__init__(self, 'Check Memory status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__snmp_executor = SNMPExecutor(self.__logger, self.__status_builder, self.__parser, self.__oid)
        self.__snmp_executor.add_args()

        self.__parser.add_argument('-m', '--memory', dest='memory', required=True,
                                   type=int, help='Number of the Memory to check')

        self.__parser.add_argument('-w', '--warning-total', dest='warningtotal', required=False,
                                   type=int, help='Warning usage (%) for total memory')
        self.__parser.add_argument('-c', '--critical-total', dest='criticaltotal', required=False,
                                   type=int, help='Critical usage (%) for total memory')
        self.__parser.add_argument('--ignore-total', dest='ignoretotal', required=False,
                                   default=False, action='store_true', help='Ignore the total memory check')

        self.__parser.add_argument('--warning-swap', dest='warningswap', required=False,
                                   type=int, help='Warning usage (%) for swap memory')
        self.__parser.add_argument('--critical-swap', dest='criticalswap', required=False,
                                   type=int, help='Critical usage (%) for swap memory')
        self.__parser.add_argument('--ignore-swap', dest='ignoreswap', required=False,
                                   default=False, action='store_true', help='Ignore the swap check')

        self.__parser.add_argument('--warning-swap-txt', dest='warningswaptxt', required=False,
                                   type=int, help='Warning usage (%) for swaptxt memory')
        self.__parser.add_argument('--critical-swap-txt', dest='criticalswaptxt', required=False,
                                   type=int, help='Critical usage (%) for swaptxt memory')
        self.__parser.add_argument('--ignore-swap-txt', dest='ignoreswaptxt', required=False,
                                   default=False, action='store_true', help='Ignore the swap txt check')

        self.__parser.add_argument('--warning-real', dest='warningreal', required=False,
                                   type=int, help='Warning usage (%) for real memory')
        self.__parser.add_argument('--critical-real', dest='criticalreal', required=False,
                                   type=int, help='Critical usage (%) for real memory')
        self.__parser.add_argument('--ignore-real', dest='ignorereal', required=False,
                                   default=False, action='store_true', help='Ignore the real memory check')

        self.__parser.add_argument('--warning-real-txt', dest='warningrealtxt', required=False,
                                   type=int, help='Warning usage (%) for realtxt memory')
        self.__parser.add_argument('--critical-real-txt', dest='criticalrealtxt', required=False,
                                   type=int, help='Critical usage (%) for realtxt memory')
        self.__parser.add_argument('--ignore-real-txt', dest='ignorerealtxt', required=False,
                                   default=False, action='store_true', help='Ignore the reaö txt check')

        self.__parser.add_argument('--warning-shared', dest='warningshared', required=False,
                                   type=int, help='Warning usage (%) for shared memory')
        self.__parser.add_argument('--critical-shared', dest='criticalshared', required=False,
                                   type=int, help='Critical usage (%) for shared memory')
        self.__parser.add_argument('--check-shared', dest='checkshared', required=False,
                                   default=False, action='store_true', help='Check the shared memory')

        self.__parser.add_argument('--warning-buffer', dest='warningbuffer', required=False,
                                   type=int, help='Warning usage (%) for buffer memory')
        self.__parser.add_argument('--critical-buffer', dest='criticalbuffer', required=False,
                                   type=int, help='Critical usage (%) for buffer memory')
        self.__parser.add_argument('--check-buffer', dest='checkbuffer', required=False,
                                   default=False, action='store_true', help='Check the buffer')

        self.__parser.add_argument('--warning-cache', dest='warningcache', required=False,
                                   type=int, help='Warning usage (%) for cache memory')
        self.__parser.add_argument('--critical-cache', dest='criticalcache', required=False,
                                   type=int, help='Critical usage (%) for cache memory')
        self.__parser.add_argument('--check-cache', dest='checkcache', required=False,
                                   default=False, action='store_true', help='Check the cache')

        self.__parser.add_argument('--warning-min-swap', dest='warningminswap', required=False,
                                   type=int, help='Warning usage (%) for minswap memory')
        self.__parser.add_argument('--critical-min-swap', dest='criticalminswap', required=False,
                                   type=int, help='Critical usage (%) for minswap memory')
        self.__parser.add_argument('--check-min-swap', dest='checkminswap', required=False,
                                   default=False, action='store_true', help='Check the minimum swap')

    def configure(self, args):
        self.__snmp_executor.configure(args)
        self.__memory_id = args.memory
        self.__warning_total = args.warningtotal
        self.__critical_total = args.criticaltotal
        self.__check_total = not args.ignoretotal

        self.__warning_swap = args.warningswap
        self.__critical_swap = args.criticalswap
        self.__check_swap = not args.ignoreswap
        self.__warning_swap_txt = args.warningswaptxt
        self.__critical_swap_txt = args.criticalswaptxt
        self.__check_swap_txt = not args.ignoreswaptxt

        self.__warning_real = args.warningreal
        self.__critical_real = args.criticalreal
        self.__check_real = not args.ignorereal
        self.__warning_real_txt = args.warningrealtxt
        self.__critical_real_txt = args.criticalrealtxt
        self.__check_real_txt = not args.ignorerealtxt

        self.__warning_shared = args.warningshared
        self.__critical_shared = args.criticalshared
        self.__check_shared = args.checkshared

        self.__warning_buffer = args.warningbuffer
        self.__critical_buffer = args.criticalbuffer
        self.__check_buffer = args.checkbuffer

        self.__warning_cache = args.warningcache
        self.__critical_cache = args.criticalcache
        self.__check_cache = args.checkcache

        self.__warning_min_swap = args.warningminswap
        self.__critical_min_swap = args.criticalminswap
        self.__check_min_swap = args.checkminswap

        success = self.__check_bounds(self.__warning_total, self.__critical_total, 'total memory')
        success = self.__check_bounds(self.__warning_swap, self.__critical_swap, 'swap') and success
        success = self.__check_bounds(self.__warning_swap_txt, self.__critical_swap_txt, 'swap txt') and success
        success = self.__check_bounds(self.__warning_real, self.__critical_real, 'real') and success
        success = self.__check_bounds(self.__warning_real_txt, self.__critical_real_txt, 'real txt') and success
        success = self.__check_bounds(self.__warning_shared, self.__critical_shared, 'shared') and success
        success = self.__check_bounds(self.__warning_buffer, self.__critical_buffer, 'buffer') and success
        success = self.__check_bounds(self.__warning_cache, self.__critical_cache, 'cache') and success
        success = self.__check_bounds(self.__warning_min_swap, self.__critical_min_swap, 'min swap') and success

        if not success:
            self.__status_builder.exit()

    def __check_bounds(self, warning, critical, name):
        success = True
        if None is not critical:
            if critical > 100:
                self.__status_builder.unknown(Output(f'Critical value for {name} can\'t be greater than 100 %'))
                success = False
            elif critical < 0:
                self.__status_builder.unknown(Output(f'Critical value for {name} must be at least 0 %'))
                success = False

        if None is not warning:

            if warning < 0:
                self.__status_builder.unknown(Output(f'Warning value for {name} must be at least 0 %'))
                success = False

        if None is not critical and None is warning:
            self.__status_builder.unknown(
                Output(f'If you set a critical bound for {name} you have to specify a warning bound'))
            success = False
        elif None is critical and None is not warning:
            self.__status_builder.unknown(
                Output(f'If you set a warning bound for {name} you have to specify a critical bound'))
            success = False
        elif None is not critical and None is not warning:
            if warning > critical:
                self.__status_builder.unknown(Output(f'Warning value for {name} can\'t be greater than critical value'))
                success = False

        return success

    def run(self):
        oids = self.__snmp_executor.run()
        status_data = {}

        keys = {
            '2': 'name',
            '3': 'totalSwap',
            '4': 'availableSwap',
            '5': 'totalReal',
            '6': 'availableReal',
            '7': 'totalSwapTXT',
            '8': 'availableSwapTXT',
            '9': 'totalRealTXT',
            '10': 'availableRealTXT',
            '11': 'totalFree',
            '12': 'minSwap',
            '13': 'shared',
            '14': 'buffer',
            '15': 'cached',
            '16': 'usedSwapTXT',
            '17': 'usedRealTXT',
            '100': 'swapError',
            '101': 'swapErrorMsg',
        }

        for oid in oids:
            base = oid['oid'].split('.')
            id = int(base[1])

            if int(base[1]) != self.__memory_id:
                continue

            data = status_data.get(id, {})
            data[keys.get(base[0])] = oid['value']
            status_data[id] = data

        if 0 == len(status_data):
            self.__status_builder.unknown(
                Output(f'Memory "{self.__memory_id}" either does not exist or not accessible'))
            self.__status_builder.exit()

        for status_data_id in status_data:
            data = status_data[status_data_id]
            self.__check_data(data, 'Swap', 'Swap', self.__warning_swap, self.__critical_swap, self.__check_swap)
            self.__check_data(data, 'SwapTXT', 'Swap txt', self.__warning_swap_txt, self.__critical_swap_txt,
                              self.__check_swap_txt)

            self.__check_data(data, 'Real', 'Real', self.__warning_real, self.__critical_real, self.__check_real)
            self.__check_data(data, 'RealTXT', 'Real txt', self.__warning_real_txt, self.__critical_real_txt,
                              self.__check_real_txt)

            total = data.get('totalSwap', 0) + data.get('totalSwapTXT', 0) + data.get('totalReal', 0) + data.get(
                'totalRealTXT', 0)
            self.__check_data(
                {'totalTotal': total, 'availableTotal': total - data['totalFree'], 'name': data['name']},
                'Total', 'Total', self.__warning_total, self.__critical_total, self.__check_total)

            self.__check_value('shared', 'Shared', data, self.__warning_shared, self.__critical_shared,
                               self.__check_shared)
            self.__check_value('buffer', 'Buffer', data, self.__warning_buffer, self.__critical_buffer,
                               self.__check_buffer)
            self.__check_value('cached', 'Cached', data, self.__warning_cache, self.__critical_cache,
                               self.__check_cache)
            self.__check_value('minSwap', 'Min SWAP', data, self.__warning_min_swap, self.__critical_min_swap,
                               self.__check_min_swap)

            if 0 != data['swapError']:
                self.__status_builder.critical(Output(f'Got an unexpected SWAP error "{data["swapErrorMessage"]}" '
                                                      f'(code {data["swapError"]})'))

    def __check_value(self, suffix, name, data, warning, critical, check):

        if not check:
            return

        self.__logger.debug(f'Check memory {suffix}')
        value = data.get(suffix, None)

        if value is None:
            self.__status_builder.unknown(
                Output(f"Couldn't check {name} because it either not exist or is not accessible "
                       f"(value not found).|{suffix}=0;0;0;0;0"))
            return

        perfdata = f";;;" if None is warning else f"{warning};{critical};;"

        output = f"Memory \"{name}\";| {suffix}={value};{perfdata}"

        if None is warning:
            self.__status_builder.success(output)
        else:
            if critical <= value:
                self.__status_builder.critical(output)
            elif self.__warning_total <= value:
                self.__status_builder.warning(output)
            else:
                self.__status_builder.success(output)

    def __check_data(self, data, suffix, name, warning, critical, check):

        if not check:
            return

        self.__logger.debug(f'Check memory {suffix}')
        total = data.get('total' + suffix, None)
        available = data.get('available' + suffix, None)

        perfdata = [
            Perfdata(f'{suffix}', 0, unit='B', warning=0, critical=0, min=0, max=0),
        ]

        if total is None:
            self.__status_builder.unknown(
                Output(f"Couldn't check {name} because it either not exist or is not accessible "
                       f"(total value not found).", perfdata))
            return
        if available is None:
            self.__status_builder.unknown(
                Output(f"Couldn't check {name} because it either not exist or is not accessible "
                       f"(available value not found).", perfdata))
            return

        used = total - available

        if None is warning:
            perfdata = [
                Perfdata(f'{suffix}', used, unit='B', warning=0, critical=0, min=0, max=total),
            ]
        else:
            perfdata = [
                Perfdata(f'{suffix}', used, unit='B', warning=warning / 100 * total, critical=critical / 100 * total,
                         min=0, max=total),
            ]

        output = Output(f"Memory \"{name}\"", perfdata)

        if None is warning:
            self.__status_builder.success(output)
        else:
            usage = used / total * 100
            if critical <= usage:
                self.__status_builder.critical(output)
            elif self.__warning_total <= usage:
                self.__status_builder.warning(output)
            else:
                self.__status_builder.success(output)
