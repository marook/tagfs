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

from tagfs.node_root import RootDirectoryNode

from tagfs_test.node_asserter import validateDirectoryInterface, validateLinkInterface
from tagfs_test.item_mock import ItemMock

class ItemAccessMock(object):

    def __init__(self):
        self.parseTime = 42
        
    def createItems(self, itemNames):
        self.taggedItems = [ItemMock(name, []) for name in itemNames]
        
class AbstractRootDirectoryNodeTest(TestCase):

    @property
    def _itemNames(self):
        return self._taggedItemNames
    
    def setUp(self):
        self._taggedItemNames = ['item1']

        self.itemAccess = ItemAccessMock()
        self.itemAccess.createItems(self._itemNames)

        self.node = RootDirectoryNode(self.itemAccess)

class TestRootDirectoryNode(AbstractRootDirectoryNodeTest):

    @property
    def _itemNames(self):
        return self._taggedItemNames + ['.untagged']

    def testNodeAttrMTimeIsItemAccessParseTime(self):
        attr = self.node.attr

        self.assertEqual(self.itemAccess.parseTime, attr.st_mtime)

    def testNodeIsDirectory(self):
        validateDirectoryInterface(self, self.node)

    def testItemLinksReplaceUntaggedDirectory(self):
        untaggedNode = self.node.entries['.untagged']

        # untagged node must be a link as the untagged directory node
        # weights less than the '.untagged' item from the tagged items.
        validateLinkInterface(self, untaggedNode)

    def testNodeContainerContainsTaggedNodeLinks(self):
        entries = self.node.entries

        for itemName in self._taggedItemNames:
            self.assertTrue(itemName in entries)

            validateLinkInterface(self, entries[itemName])

class TestRootDirectoryNodeUntaggedDirectory(AbstractRootDirectoryNodeTest):

    def testNodeContainsUntaggedDirectory(self):
        untaggedNode = self.node.entries['.untagged']

        validateDirectoryInterface(self, untaggedNode)
