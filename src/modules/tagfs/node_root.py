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

from node_filter import FilterDirectoryNode
from node_untagged_items import UntaggedItemsDirectoryNode

class RootDirectoryNode(FilterDirectoryNode):

    def __init__(self, itemAccess, config):
        super(RootDirectoryNode, self).__init__(itemAccess, config)

    @property
    def items(self):
        return self.itemAccess.taggedItems

    @property
    def _enableItemLinks(self):
        return self.config.enableRootItemLinks

    @property
    def _entries(self):
        yield UntaggedItemsDirectoryNode('.untagged', self.itemAccess)

        for e in super(RootDirectoryNode, self)._entries:
            yield e
