#
# Copyright 2010 Markus Pielmeier
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

import unittest
import logging
import env

from tagfs import config

import setup

class TestConfig(unittest.TestCase):

    def configs(self):
        for dir in setup.validItemDirectories:
            yield config.Config(dir)

    def testConfig(self):
        for c in self.configs():
            logging.debug('Testing config %s' % c)

            self.assertTrue(isinstance(c.tagFileName, str))
            self.assertTrue(isinstance(c.enableValueFilters, bool))
            self.assertTrue(isinstance(c.enableRootItemLinks, bool))

            c.enableValueFilters = True
            self.assertTrue(isinstance(c.enableValueFilters, bool))
            self.assertEqual(True, c.enableValueFilters)
