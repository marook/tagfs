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
from tagfs.node import Stat, ItemLinkEntry
import stat

class UntaggedItemsDirectoryEntry(object):
    
    def __init__(self, name, itemAccess):
        self.itemAccess = itemAccess

    @property
    def attr(self):
        s = Stat()

        s.st_mode = stat.S_IFDIR | 0555
        # TODO why nlink == 2?
        s.st_nlink = 2
        # TODO write test case which tests st_mtime == itemAccess.parseTime
        s.st_mtime = self.itemAccess.parseTime
        s.st_ctime = s.st_mtime
        s.st_atime = s.st_mtime

        return s

    @property
    def entries(self):
        return dict([[item.name, ItemLinkEntry(item)] for item in self.itemAccess.untaggedItems])

class UntaggedItemsContainerNode(object):

    def __init__(self, itemAccess):
        self.itemAccess = itemAccess

    def getEntry(self, name):
        return UntaggedItemsDirectoryEntry(name, self.itemAccess)
