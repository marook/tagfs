#!/usr/bin/env python
#
# Copyright 2009, 2010 Markus Pielmeier
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
#
# = tag fs =
# == glossary ==
# * item: An item is a directory in the item container directory. Items can be
# tagged using a tag file.
# * tag: A tag is a text string which can be assigned to an item. Tags can
# consist of any character except newlines.

import os
import stat
import errno
import exceptions
import time
import functools
import logging

import fuse
if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."
fuse.fuse_python_api = (0, 2)

from view import View
from cache import cache
from item_access import ItemAccess
from config import parseConfig
from log import logException

import sysIO
import freebase_support
    
class TagFS(fuse.Fuse):

    def __init__(self, initwd, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        
        self._initwd = initwd
        self._itemsRoot = None

        # TODO change command line arguments structure
        # goal: tagfs <items dir> <mount dir>
        self.parser.add_option('-i',
                               '--items-dir',
                               dest = 'itemsDir',
                               help = 'items directory',
                               metavar = 'dir')
        self.parser.add_option('-t',
                               '--tag-file',
                               dest = 'tagFileName',
                               help = 'tag file name',
                               metavar = 'file',
                               default = None)
        self.parser.add_option('--value-filter',
                               action = 'store_true',
                               dest = 'enableValueFilters',
                               help = 'Displays value filter directories on toplevel instead of only context entries',
                               default = None)
        self.parser.add_option('--root-items',
                               action = 'store_true',
                               dest = 'enableRootItemLinks',
                               help = 'Display item links in tagfs root directory.',
                               default = None)

    def getItemAccess(self):
        # Maybe we should move the parser run from main here.
        # Or we should at least check if it was run once...
        opts, args = self.cmdline

        # Maybe we should add expand user? Maybe even vars???
        assert opts.itemsDir != None and opts.itemsDir != ''
        itemsRoot = os.path.normpath(
                os.path.join(self._initwd, opts.itemsDir))

        # TODO rel https://github.com/marook/tagfs/issues#issue/2
        # Ensure that mount-point and items dir are disjoined.
        # Something along
        # assert not os.path.normpath(itemsDir).startswith(itemsRoot)
        
        # try/except here?
        try:
            return ItemAccess(sysIO.createSystem(), itemsRoot, self.config.tagFileName, freebase_support.QueryParser(), freebase_support.FreebaseAdapter())
        except OSError, e:
            logging.error("Can't create item access from items directory %s. Reason: %s",
                    itemsRoot, str(e.strerror))
            raise
    
    @property
    @cache
    def config(self):
        opts, args = self.cmdline

        c = parseConfig(os.path.normpath(os.path.join(self._initwd, opts.itemsDir)))

        if opts.tagFileName:
            c.tagFileName = opts.tagFileName

        if opts.enableValueFilters:
            c.enableValueFilters = opts.enableValueFilters

        if opts.enableRootItemLinks:
            c.enableRootItemLinks = opts.enableRootItemLinks

        logging.debug('Using configuration %s' % c)

        return c

    @property
    @cache
    def view(self):
        itemAccess = self.getItemAccess()

        return View(itemAccess, self.config)

    @logException
    def getattr(self, path):
        return self.view.getattr(path)

    @logException
    def readdir(self, path, offset):
        return self.view.readdir(path, offset)
            
    @logException
    def readlink(self, path):
        return self.view.readlink(path)

    @logException
    def open(self, path, flags):
        return self.view.open(path, flags)

    @logException
    def read(self, path, size, offset):
        return self.view.read(path, size, offset)

    @logException
    def write(self, path, data, pos):
        return self.view.write(path, data, pos)

    @logException
    def symlink(self, path, linkPath):
        return self.view.symlink(path, linkPath)

def main():
    fs = TagFS(os.getcwd(),
            version = "%prog " + fuse.__version__,
            dash_s_do = 'setsingle')

    fs.parse(errex = 1)
    opts, args = fs.cmdline

    if opts.itemsDir == None:
        fs.parser.print_help()
        # items dir should probably be an arg, not an option.
        print "Error: Missing items directory option."
        # Quickfix rel https://github.com/marook/tagfs/issues/#issue/3
        # FIXME: since we run main via sys.exit(main()), this should
        #        probably be handled via some return code.
        import sys
        sys.exit()
        
    return fs.main()

if __name__ == '__main__':
    import sys
    sys.exit(main())
