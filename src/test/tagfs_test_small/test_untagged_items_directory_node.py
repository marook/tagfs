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
from tagfs.node_untagged_items import UntaggedItemsDirectoryNode
from tagfs_test.node_asserter import validateLinkInterface, validateDirectoryInterface

class ItemMock(object):

    def __init__(self, name):
        self.name = name

class ItemAccessMock(object):

    def __init__(self):
        self.parseTime = 42
        self.untaggedItems = [ItemMock(name) for name in ['item1', 'item2']]

class TestUntaggedItemsDirectoryNode(TestCase):

    def setUp(self):
        self.itemAccess = ItemAccessMock()
        self.nodeName = 'e'
        self.node = UntaggedItemsDirectoryNode(self.nodeName, self.itemAccess)

    def testNodeAttrMTimeIsItemAccessParseTime(self):
        attr = self.node.attr

        self.assertEqual(self.itemAccess.parseTime, attr.st_mtime)

    def testNodeIsDirectory(self):
        validateDirectoryInterface(self, self.node)

    def testUntaggedItemAccessItemsAreUntaggedItemsDirectoryEntries(self):
        entries = self.node.entries

        self.assertEqual(len(self.itemAccess.untaggedItems), len(entries))

        for i in self.itemAccess.untaggedItems:
            self.assertTrue(i.name in entries)

            validateLinkInterface(self, entries[i.name])

    def testNodeHasName(self):
        self.assertEqual(self.nodeName, self.node.name)
