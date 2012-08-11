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

from tagfs.node_filter import FilterDirectoryNode

class ValueFilterDirectoryNode(FilterDirectoryNode):

    def __init__(self, itemAccess, config, parentNode, value):
        super(ValueFilterDirectoryNode, self).__init__(itemAccess, config)
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
    
