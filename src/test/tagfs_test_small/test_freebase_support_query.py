#
# Copyright 2012 Markus Pielmeier
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

import unittest
import tagfs.freebase_support as freebase_support

class WhenQueryWithOneFilerAndOneSelector(unittest.TestCase):

    def setUp(self):
        super(WhenQueryWithOneFilerAndOneSelector, self).setUp()

        self.query = freebase_support.Query({'filter': 'filterValue', 'selector': None, })

    def testThenSelectedKeysIsSelector(self):
        self.assertEqual(list(self.query.selectedKeys), ['selector',])

    def testThenQueryStringIs(self):
        self.assertEqual(self.query.queryString, '{"filter":"filterValue","selector":[]}')
