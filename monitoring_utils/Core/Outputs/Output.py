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


class Output:

    def __init__(self, description: str, perfdata=[]):

        self._description = description
        self._perfdata = perfdata

    def __str__(self) -> str:
        return self.get()

    def __repr__(self) -> str:
        return self.get()

    def get(self) -> str:
        output = self._description

        if 0 != len(self._perfdata):
            output += ' |'

        for perfdata in self._perfdata:
            output += f"{perfdata.get_label()}={perfdata.get_value()}{perfdata.get_unit() if None is not perfdata.get_unit() else ''};"

            if None is perfdata.get_warning():
                output += ';'
            else:
                output += str(perfdata.get_warning()) + ';'

            if None is perfdata.get_critical():
                output += ';'
            else:
                output += str(perfdata.get_critical()) + ';'

            if None is perfdata.get_min():
                output += ';'
            else:
                output += str(perfdata.get_min()) + ';'

            if None is not perfdata.get_max():
                output += str(perfdata.get_max())

            output += ' '

        return output
