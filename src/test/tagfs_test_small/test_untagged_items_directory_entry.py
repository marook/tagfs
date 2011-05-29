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
import stat
from tagfs.node_untagged_items import UntaggedItemsDirectoryEntry
from tagfs_test.entry_asserter import validateFileEntryInterface

def attrIsDirectory(attr):
    return (attr.st_mode & stat.S_IFDIR != 0)

class ItemMock(object):

    def __init__(self, name):
        self.name = name

class ItemAccessMock(object):

    def __init__(self):
        self.parseTime = 42
        self.untaggedItems = [ItemMock(name) for name in ['item1', 'item2']]

class TestUntaggedItemsDirectoryEntry(TestCase):

    def setUp(self):
        self.itemAccess = ItemAccessMock()

    def testEntryAttrMTimeIsItemAccessParseTime(self):
        attr = UntaggedItemsDirectoryEntry('e', self.itemAccess).attr

        self.assertEqual(self.itemAccess.parseTime, attr.st_mtime)

    def testEntryAttrModeIsDirectory(self):
        attr = UntaggedItemsDirectoryEntry('e', self.itemAccess).attr

        self.assertTrue(attrIsDirectory(attr))

    def testUntaggedItemAccessItemsAreUntaggedItemsDirectoryEntries(self):
        entries = UntaggedItemsDirectoryEntry('e', self.itemAccess).entries

        self.assertEqual(len(self.itemAccess.untaggedItems), len(entries))

        for i in self.itemAccess.untaggedItems:
            self.assertTrue(i.name in entries)

            validateFileEntryInterface(self, entries[i.name])
