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

from cache import cache
from node import Stat, ItemLinkNode, DirectoryNode
from node_filter import FilterDirectoryNode
from node_untagged_items import UntaggedItemsDirectoryNode

class AnyContextValueFilterDirectoryNode(FilterDirectoryNode):

    def __init__(self, itemAccess, config, parentNode, value):
        super(AnyContextValueFilterDirectoryNode, self).__init__(itemAccess, config)
        self.parentNode = parentNode
        self.value = value

    @property
    def name(self):
        return self.value

    @property
    def items(self):
        for item in self.parentNode.items:
            if not item.isTaggedWithValue(self.value):
                continue

            yield item
    
class AnyContextValueListDirectoryNode(DirectoryNode):

    def __init__(self, itemAccess, config, parentNode):
        self.itemAccess = itemAccess
        self.config = config
        self.parentNode = parentNode

    @property
    def name(self):
        return '.any_context'

    @property
    def attr(self):
        s = super(AnyContextValueListDirectoryNode, self).attr

        # TODO why nlink == 2?
        s.st_nlink = 2

        # TODO write test case which tests st_mtime == itemAccess.parseTime
        s.st_mtime = self.itemAccess.parseTime
        s.st_ctime = s.st_mtime
        s.st_atime = s.st_mtime

        return s

    @property
    def items(self):
        return self.parentNode.items

    @property
    def contextValues(self):
        values = set()

        for item in self.parentNode.items:
            for v in item.values:
                values.add(v)

        return values

    @property
    def _entries(self):
        for value in self.contextValues:
            yield AnyContextValueFilterDirectoryNode(self.itemAccess, self.config, self, value)

    def addsValue(self, parentItems):
        if(super(AnyContextValueListDirectoryNode, self).addsValue(parentItems)):
            return True

        for e in self._entries:
            if(e.addsValue(parentItems)):
                return True

        return False
