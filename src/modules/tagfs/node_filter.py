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

from cache import cache
from node import Stat, ItemLinkNode, DirectoryNode
from node_export import ExportDirectoryNode

class FilterDirectoryNode(DirectoryNode):
    
    def __init__(self, itemAccess, config):
        self.itemAccess = itemAccess
        self.config = config

    @property
    def attr(self):
        s = super(FilterDirectoryNode, self).attr

        # TODO why nlink == 2?
        s.st_nlink = 2

        # TODO write test case which tests st_mtime == itemAccess.parseTime
        s.st_mtime = self.itemAccess.parseTime
        s.st_ctime = s.st_mtime
        s.st_atime = s.st_mtime

        return s

    @property
    def contexts(self):
        c = set()

        for item in self.items:
            for t in item.tags:
                context = t.context

                if context is None:
                    continue

                c.add(context)

        return c

    @property
    def _enableItemLinks(self):
        return True

    @property
    def _entries(self):
        # the import is not global because we want to prevent a cyclic
        # dependency (ugly but works)
        from node_filter_context import ContextValueListDirectoryNode
        from node_filter_value import ValueFilterDirectoryNode
        from node_filter_any_context import AnyContextValueListDirectoryNode

        yield ExportDirectoryNode(self.itemAccess, self)

        yield AnyContextValueListDirectoryNode(self.itemAccess, self.config, self)

        if(self.config.enableValueFilters):
            for value in self.itemAccess.values:
                yield ValueFilterDirectoryNode(self.itemAccess, self.config, self, value)

        for context in self.contexts:
            yield ContextValueListDirectoryNode(self.itemAccess, self.config, self, context)

        if(self._enableItemLinks):
            for item in self.items:
                yield ItemLinkNode(item)

    def addsValue(self, parentItems):
        itemsLen = len(list(self.items))
        if(itemsLen == 0):
            return False

        # TODO we should not compare the lengths but whether the child and
        # parent items are different
        parentItemsLen = len(list(parentItems))

        return itemsLen != parentItemsLen

    def _addsValue(self, child):
        return child.addsValue(self.items)
