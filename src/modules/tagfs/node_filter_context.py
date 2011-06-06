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

from tagfs.cache import cache
from tagfs.node import Stat, ItemLinkNode, DirectoryNode
from tagfs.node_filter import FilterDirectoryNode
from tagfs.node_untagged_items import UntaggedItemsDirectoryNode

class ContextValueFilterDirectoryNode(FilterDirectoryNode):

    def __init__(self, itemAccess, parentNode, context, value):
        super(ContextValueFilterDirectoryNode, self).__init__(itemAccess)
        self.parentNode = parentNode
        self.context = context
        self.value = value

    @property
    def name(self):
        return self.value

    @property
    def items(self):
        for item in self.parentNode.items:
            if not item.isTaggedWithContextValue(self.context, self.value):
                continue

            yield item
    
class ContextValueListDirectoryNode(DirectoryNode):
    
    def __init__(self, itemAccess, parentNode, context):
        self.itemAccess = itemAccess
        self.parentNode = parentNode
        self.context = context

    @property
    def name(self):
        return self.context

    @property
    def attr(self):
        s = super(ContextValueListDirectoryNode, self).attr

        # TODO why nlink == 2?
        s.st_nlink = 2

        # TODO write test case which tests st_mtime == itemAccess.parseTime
        s.st_mtime = self.itemAccess.parseTime
        s.st_ctime = s.st_mtime
        s.st_atime = s.st_mtime

        return s

    @property
    def items(self):
        for item in self.parentNode.items:
            if not item.isTaggedWithContext(self.context):
                continue

            yield item

    @property
    def contextValues(self):
        values = set()

        for item in self.parentNode.items:
            for tag in item.getTagsByContext(self.context):
                values.add(tag.value)

        return values

    @property
    def _entries(self):
        for value in self.contextValues:
            yield ContextValueFilterDirectoryNode(self.itemAccess, self, self.context, value)
