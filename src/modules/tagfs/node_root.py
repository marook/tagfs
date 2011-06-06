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
from tagfs.node import Stat, ItemLinkNode
from tagfs.node_filter import FilterDirectoryNode
from tagfs.node_untagged_items import UntaggedItemsDirectoryNode
from tagfs.node_filter_context import ContextValueListDirectoryNode

class RootDirectoryNode(FilterDirectoryNode):
    
    def __init__(self, itemAccess):
        super(RootDirectoryNode, self).__init__(itemAccess)

    @property
    def items(self):
        return self.itemAccess.taggedItems

    @property
    def _entries(self):
        yield UntaggedItemsDirectoryNode('.untagged', self.itemAccess)

        for e in super(RootDirectoryNode, self)._entries:
            yield e
