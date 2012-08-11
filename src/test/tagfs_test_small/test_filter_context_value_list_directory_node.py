#
# Copyright 2011 Markus Pielmeier
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

from tagfs.node_filter_context import ContextValueListDirectoryNode

from tagfs_test.node_asserter import validateDirectoryInterface, validateLinkInterface
from tagfs_test.item_access_mock import ItemAccessMock
from tagfs_test.item_mock import createItemMocks

class ParentNodeMock(object):

    pass

class TestContextValueListDirectoryNode(TestCase):

    def setUp(self):
        self.itemAccess = ItemAccessMock()
        self.itemAccess.taggedItems = createItemMocks(['item1'])

        self.parentNode = ParentNodeMock()
        self.context = 'c1'
        self.node = ContextValueListDirectoryNode(self.itemAccess, None, self.parentNode, self.context)

    def testNodeAttrMTimeIsItemAccessParseTime(self):
        attr = self.node.attr

        self.assertEqual(self.itemAccess.parseTime, attr.st_mtime)

    def testNodeIsDirectory(self):
        validateDirectoryInterface(self, self.node)
