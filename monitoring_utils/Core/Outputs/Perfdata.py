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


class Perfdata:

    def __init__(self, label: str, value, unit=None, warning=None, critical=None, min=None, max=None):
        self._max = max
        self._min = min
        self._critical = critical
        self._warning = warning
        self._unit = unit
        self._value = value
        self._label = label

    def get_max(self):
        return self._max

    def get_min(self):
        return self._min

    def get_critical(self):
        return self._critical

    def get_warning(self):
        return self._warning

    def get_unit(self):
        return self._unit

    def get_value(self):
        return self._value

    def get_label(self):
        return self._label
