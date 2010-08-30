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

class Config(ConfigParser.SafeConfigParser):

    def __init__(self, itemsDir):
        super(self, Config).__init__({
                'tagFileName': '.tag',
                'enableValueFilters': False,
                'enableRootItemLinks': False,
                })

        self.itemsDir = itemsDir

        self.read([os.path.join(itemsDir, '.tagfs', 'tagfs.conf'),
                   os.path.expanduser(os.path.join('~', '.tagfs', 'tagfs.conf')),
                   os.path.join('/', 'etc', 'tagfs', 'tagfs.conf')])

    @property
    def tagFileName(self):
        return self.get('global', 'tagFileName')

    # TODO implement generic approach to get/set boolean values
    @property
    def enableValueFilters(self):
        return self.getboolean('global', 'enableValueFilters')

    @enableValueFilters.setter
    def enableValueFilters(self, enableValueFilters):
        self.set('global', 'enableValueFilters', enableValueFilters)

    @property
    def enableRootItemLinks(self):
        return self.getboolean('global', 'enableRootItemLinks')

    @enableValueFilters.setter
    def enableRootItemLinks(self, enableRootItemLinks):
        self.set('global', 'enableRootItemLinks', enableRootItemLinks)
