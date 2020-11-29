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
from monitoring_utils.Checks.NMAP.Scripts.SSLEnumCiphers import SSLEnumCiphers
from monitoring_utils.Core.Executor.NMAPExecutor import NMAPExecutor
from monitoring_utils.Core.Executor.NmapScriptExecutor import NmapScriptExecutor
from monitoring_utils.Core.Plugin.Plugin import Plugin


class Ciphers(Plugin):

    def __init__(self):
        self.__logger = None
        self.__status_builder = None
        self.__parser = None
        self.__executor = None
        self.__cipher_script = None

        self.__expected = None
        self.__host = None
        self.__allowed_tlsv1_0_ciphers = None
        self.__allowed_tlsv1_1_ciphers = None
        self.__allowed_tlsv1_2_ciphers = None
        self.__allowed_tlsv1_3_ciphers = None
        self.__least_tlsv1_0_strength = None
        self.__least_tlsv1_1_strength = None
        self.__least_tlsv1_2_strength = None
        self.__least_tlsv1_3_strength = None
        self.__least_strength = None
        self.__least_strength_overall = None
        self.__ignoreciphername = None
        self.__ignorecipherstrength = None
        self.__ignorestrength = None

        self.__report = None
        self.__runtime = None
        self.__stats = None
        self.__open_ports = []
        self.__ignore_port = []

        Plugin.__init__(self, 'Check DNSSEC status')

    def add_args(self):
        self.__parser = self.get_parser()
        self.__logger = self.get_logger()
        self.__status_builder = self.get_status_builder()
        self.__cipher_script = SSLEnumCiphers(self.__logger, self.__status_builder)
        self.__executor = NMAPExecutor(self.__logger, self.__parser, self.__status_builder,
                                       scripts=['ssl-enum-ciphers'], only_tcp=True)
        self.__executor.add_args()

        self.__parser.add_argument('--allowed-tlsv1-0-ciphers', dest='allowedtlsv10ciphers', action='append',
                                   help='Allowed TLSv1.0 chippers. Format: PORT:NAME[,NAME[,NAME ...]]',
                                   default=[])
        self.__parser.add_argument('--allowed-tlsv1-1-ciphers', dest='allowedtlsv11ciphers', action='append',
                                   help='Allowed TLSv1.1 chippers. Format: PORT:NAME[,NAME[,NAME ...]]',
                                   default=[])
        self.__parser.add_argument('--allowed-tlsv1-2-ciphers', dest='allowedtlsv12ciphers', action='append',
                                   help='Allowed TLSv1.2 chippers. Format: PORT:NAME[,NAME[,NAME ...]]',
                                   default=[])
        self.__parser.add_argument('--allowed-tlsv1-3-ciphers', dest='allowedtlsv13ciphers', action='append',
                                   help='Allowed TLSv1.3 chippers. Format: PORT:NAME[,NAME[,NAME ...]]',
                                   default=[])

        self.__parser.add_argument('--least-tlsv1-0-strength', dest='leasttlsv10strength', default=[], action='append',
                                   help='Least strength of TLSv1.0 chippers. Format: PORT:STRENGTH')
        self.__parser.add_argument('--least-tlsv1-1-strength', dest='leasttlsv11strength', default=[], action='append',
                                   help='Least strength of TLSv1.1 chippers. Format: PORT:STRENGTH')
        self.__parser.add_argument('--least-tlsv1-2-strength', dest='leasttlsv12strength', default=[], action='append',
                                   help='Least strength of TLSv1.2 chippers. Format: PORT:STRENGTH')
        self.__parser.add_argument('--least-tlsv1-3-strength', dest='leasttlsv13strength', default=[], action='append',
                                   help='Least strength of TLSv1.3 chippers. Format: PORT:STRENGTH')

        self.__parser.add_argument('--least-strength', dest='leaststrength', default=[], action='append',
                                   help='Least strength of chippers. Format: PORT:STRENGTH')
        self.__parser.add_argument('--least-strength-overall', dest='leaststrengthoverall', default='B', type=str,
                                   help='Least strength of chippers over all ports.')

        self.__parser.add_argument('--ignore-cipher-name', dest='ignoreciphername', required=False,
                                   action='store_true', help='Ignore the cipher name comparison')
        self.__parser.add_argument('--ignore-cipher-strength', dest='ignorecipherstrength', required=False,
                                   action='store_true', help='Ignore the cipher strength comparison')
        self.__parser.add_argument('--ignore-strength', dest='ignorestrength', required=False,
                                   action='store_true', help='Ignore the strength comparison over all ports')

        self.__parser.add_argument('--ignore-port', dest='ignoreport', default=[], action='append',
                                   help='Ports to ignore')

    def configure(self, args):
        self.__executor.configure(args)
        self.__allowed_tlsv1_0_ciphers = args.allowedtlsv10ciphers
        self.__allowed_tlsv1_1_ciphers = args.allowedtlsv11ciphers
        self.__allowed_tlsv1_2_ciphers = args.allowedtlsv12ciphers
        self.__allowed_tlsv1_3_ciphers = args.allowedtlsv13ciphers

        self.__least_tlsv1_0_strength = args.leasttlsv10strength
        self.__least_tlsv1_1_strength = args.leasttlsv11strength
        self.__least_tlsv1_2_strength = args.leasttlsv12strength
        self.__least_tlsv1_3_strength = args.leasttlsv13strength

        self.__least_strength = args.leaststrength
        self.__least_strength_overall = args.leaststrengthoverall

        self.__ignoreciphername = args.ignoreciphername
        self.__ignorecipherstrength = args.ignorecipherstrength
        self.__ignorestrength = args.ignorestrength
        self.__ignore_port = args.ignoreport

        if self.__ignoreciphername and self.__ignorecipherstrength and self.__ignorestrength:
            self.__status_builder.unknown('You set --ignore-cipher-name, --ignore-cipher-strength and --ignore-strength'
                                          ' so no check can be executed.')
            self.__status_builder.exit()

        self.__cipher_script.set_allowed_tlsv1_0_ciphers(self.__allowed_tlsv1_0_ciphers)
        self.__cipher_script.set_allowed_tlsv1_1_ciphers(self.__allowed_tlsv1_1_ciphers)
        self.__cipher_script.set_allowed_tlsv1_2_ciphers(self.__allowed_tlsv1_2_ciphers)
        self.__cipher_script.set_allowed_tlsv1_3_ciphers(self.__allowed_tlsv1_3_ciphers)
        self.__cipher_script.set_least_tlsv1_0_strength(self.__least_tlsv1_0_strength)
        self.__cipher_script.set_least_tlsv1_1_strength(self.__least_tlsv1_1_strength)
        self.__cipher_script.set_least_tlsv1_2_strength(self.__least_tlsv1_2_strength)
        self.__cipher_script.set_least_tlsv1_3_strength(self.__least_tlsv1_3_strength)
        self.__cipher_script.set_least_strength(self.__least_strength)
        self.__cipher_script.set_least_strength_overall(self.__least_strength_overall)
        self.__cipher_script.set_ignore_cipher_name(self.__ignoreciphername)
        self.__cipher_script.set_ignore_cipher_strength(self.__ignorecipherstrength)
        self.__cipher_script.set_ignore_strength(self.__ignorestrength)
        self.__cipher_script.set_ignore_port(self.__ignore_port)

        self.__cipher_script.parse_config()

    def run(self):
        self.__report, self.__runtime, self.__stats = self.__executor.scan()
        if None == self.__report:
            return

        self.__cipher_script.set_report(self.__report)

        nmap_script_executor = NmapScriptExecutor(status_builder=self.__status_builder, logger=self.__logger)
        nmap_script_executor.add_script('ssl-enum-ciphers', self.__cipher_script)
        nmap_script_executor.execute(self.__executor.get_open_ports(), self.__ignore_port)

        self.__status_builder.success('All checks passed')
