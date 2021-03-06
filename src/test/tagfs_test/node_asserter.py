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

import stat

def hasMode(attr, mode):
    return (attr.st_mode & mode > 0)

def validateNodeInterface(test, node):
    attr = node.attr

    test.assertTrue(attr.st_atime >= 0)
    test.assertTrue(attr.st_mtime >= 0)
    test.assertTrue(attr.st_ctime >= 0)

def validateDirectoryInterface(test, node):
    attr = node.attr

    test.assertTrue(hasMode(attr, stat.S_IFDIR))

    validateNodeInterface(test, node)

def validateLinkInterface(test, node):
    attr = node.attr

    test.assertTrue(hasMode(attr, stat.S_IFLNK))

    validateNodeInterface(test, node)
