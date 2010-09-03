#!/usr/bin/env python
#
# Copyright 2009, 2010 Markus Pielmeier
#
# This file is part of tagfs.
#
# tagfs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tagfs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with tagfs.  If not, see <http://www.gnu.org/licenses/>.
#

import ConfigParser
import logging
import os

class Config(ConfigParser.SafeConfigParser):

    GLOBAL_SECTION = 'global'

    def applyDefaults(self):
        self.tagFileName = '.tag'
        self.enableValueFilters = False
        self.enableRootItemLinks = False

    def __init__(self, itemsDir):
        self._config = ConfigParser.SafeConfigParser({
                'tagFileName': '.tag',
                'enableValueFilters': False,
                'enableRootItemLinks': False,
                })
        self._config.add_section(Config.GLOBAL_SECTION)

        self.itemsDir = itemsDir

        self.applyDefaults()

        parsedFiles = self._config.read([os.path.join(itemsDir, '.tagfs', 'tagfs.conf'),
                                         os.path.expanduser(os.path.join('~', '.tagfs', 'tagfs.conf')),
                                         os.path.join('/', 'etc', 'tagfs', 'tagfs.conf')])

        logging.debug('Parsed the following config files: %s' % ', '.join(parsedFiles))

    @property
    def tagFileName(self):
        return self._config.get(Config.GLOBAL_SECTION, 'tagFileName')

    # TODO implement generic approach to get/set boolean values
    @property
    def enableValueFilters(self):
        return self._config.getboolean(Config.GLOBAL_SECTION, 'enableValueFilters')

    @enableValueFilters.setter
    def enableValueFilters(self, enableValueFilters):
        self._config.set(Config.GLOBAL_SECTION, 'enableValueFilters', enableValueFilters)

    @property
    def enableRootItemLinks(self):
        return self._config.getboolean(Config.GLOBAL_SECTION, 'enableRootItemLinks')

    @enableValueFilters.setter
    def enableRootItemLinks(self, enableRootItemLinks):
        self._config.set(Config.GLOBAL_SECTION, 'enableRootItemLinks', enableRootItemLinks)
