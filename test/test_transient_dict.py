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
from tagfs.transient_dict import TransientDict

class TestTransientDict(unittest.TestCase):
    
    def testGetSetIn(self):
        """Test some simple get, set an in calls.
        """

        d = TransientDict(10)

        self.assertTrue('1' not in d)

        d['1'] = 'a'
        d['2'] = 'b'

        self.assertTrue(d['1'] == 'a')
        self.assertTrue(d['2'] == 'b')

        self.assertTrue('1' in d)
        self.assertTrue('3' not in d)
        self.assertTrue('a' not in d)

    def testForgettFeature(self):
        """Test the forgett feature
        """

        d = TransientDict(1)

        d['1'] = 'a'
        d['2'] = 'b'
        d['3'] = 'c'

        self.assertTrue('1' not in d)
        self.assertTrue('3' in d)
