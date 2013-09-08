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

from tagfs.node_filter_context import ContextValueFilterDirectoryNode

from tagfs_test.node_asserter import validateDirectoryInterface, validateLinkInterface
from tagfs_test.item_access_mock import ItemAccessMock
from tagfs_test.item_mock import ItemMock

class TagMock(object):

    def __init__(self, context, value):
        self.context = context
        self.value = value

class TaggedItemMock(ItemMock):

    def __init__(self, name, context, value):
        super(TaggedItemMock, self).__init__(name, [TagMock(context, value), ])

        self._context = context
        self._value = value

    def isTaggedWithContext(self, context):
        return self._context == context

    def isTaggedWithContextValue(self, context, value):
        return self._context == context and self._value == value

    def getTagsByContext(self, context):
        if(context == self._context):
            return self.tags
        else:
            return []

class ParentNodeMock(object):

    def __init__(self, items):
        self.items = items

class ConfigMock(object):

    @property
    def enableValueFilters(self):
        return False

class TestContextValueFilterDirectoryNode(TestCase):

    def setUp(self):
        self.context = 'c1'
        self.value = 'v1'

        self.itemAccess = ItemAccessMock()
        self.itemAccess.taggedItems = [TaggedItemMock('item1', self.context, self.value), ]

        self.config = ConfigMock()

        self.parentNode = ParentNodeMock(self.itemAccess.taggedItems)
        self.node = ContextValueFilterDirectoryNode(self.itemAccess, self.config, self.parentNode, self.context, self.value)

    def testNodeAttrMTimeIsItemAccessParseTime(self):
        attr = self.node.attr

        self.assertEqual(self.itemAccess.parseTime, attr.st_mtime)

    def testNodeIsDirectory(self):
        validateDirectoryInterface(self, self.node)

    def testMatchingItemIsAvailableAsLink(self):
        e = self.node.entries['item1']

        validateLinkInterface(self, e)
