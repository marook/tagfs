#
# Copyright 2009 Markus Pielmeier
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

import fuse
import stat

class Stat(fuse.Stat):
    
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

    def __str__(self):
        return '[' + ', '.join([field + ': ' + str(self.__dict__[field]) for field in self.__dict__]) + ']'

class ItemLinkEntry(object):

    def __init__(self, item):
        self.item = item

    @property
    def name(self):
        return item.name

    @property
    def attr(self):
        s = Stat()

        s.st_mode = stat.S_IFLNK | 0444
        s.st_nlink = 2
    
        return s

    @property
    def link(self):
        return self.item.itemDirectory
