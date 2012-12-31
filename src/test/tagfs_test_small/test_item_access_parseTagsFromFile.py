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
import tagfs.item_access as item_access
import systemMocks

class ParseTagsFromFileTest(unittest.TestCase):

    def setUp(self):
        super(ParseTagsFromFileTest, self).setUp()

        self.system = systemMocks.SystemMock(self)

    def setTagFileContent(self, lines):
        self.system.readFiles['.tag'] = systemMocks.ReadLineFileMock(lines)

    def assertParseTags(self, expectedTags):
        self.assertEqual(list(item_access.parseTagsFromFile(self.system, '.tag')), expectedTags)

    def testParseTagWithoutContext(self):
        self.setTagFileContent(['value',])

        self.assertParseTags([item_access.Tag('value'),])

    def testParseTagWithContext(self):
        self.setTagFileContent(['context: value',])

        self.assertParseTags([item_access.Tag('value', 'context'),])
