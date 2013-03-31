#
# Copyright 2013 Markus Pielmeier
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

import array
import stat
from node import Stat

class FileNode(object):
    
    @property
    def attr(self):
        s = Stat()

        s.st_mode = stat.S_IFREG | 0444
        s.st_nlink = 2

        # TODO replace with memory saving size calculation
        s.st_size = len(array.array('c', self.content))

        return s

    def open(self, path, flags):
        return

    def read(self, path, size, offset):
        return self.content[offset:offset + size]
