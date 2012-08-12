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
#

from unittest import TestCase

from tagfs import item_access

class TagTest(TestCase):

    def testTagValueInfluencesHash(self):
        self.assertTrue(item_access.Tag('a', None).__hash__() != item_access.Tag('b', None).__hash__())

    def testTagContextInfluencesHash(self):
        self.assertTrue(item_access.Tag('v', None).__hash__() != item_access.Tag('v', 'c').__hash__())

    def testEqualTagsEqWhenContextNone(self):
        self.assertTrue(item_access.Tag('t', None).__eq__(item_access.Tag('t', None)))

    def testEqualTagsEqWhenContextStr(self):
        self.assertTrue(item_access.Tag('t', 'c').__eq__(item_access.Tag('t', 'c')))
