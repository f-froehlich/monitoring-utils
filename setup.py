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


from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('CHANGELOG.md') as changelog_file:
    CHANGELOG = changelog_file.read()

additional_files = [
    'README.md',
    'CHANGELOG.md',
    'LICENSE',
]

setup_args = dict(
    name='monitoring_utils',
    version='2.0.0-5',
    description='Utilities for monitoring scripts, plugins and other',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n\n' + CHANGELOG,
    license='AGPLv3',
    packages=find_packages(),
    author='Fabian Fröhlich',
    author_email='mail@confgen.org',
    keywords=['icinga', 'icinga2', 'icinga2-plugin', 'monitoring', 'check', 'nagios', 'nagios-plugin', 'nrpe',
              'healthcheck', 'serverstatus', 'security', 'security-tools'],
    url='https://github.com/f-froehlich/monitoring-utils',
    download_url='https://pypi.org/project/monitoring-utils/',
    data_files=[('monitoring_utils_doc', additional_files)]

)

install_requires = [
    'python-telegram-bot>=4.0'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
