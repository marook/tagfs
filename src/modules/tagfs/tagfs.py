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


#====================================================================
# first set up exception handling and logging

import logging
import sys

def setUpLogging():
    def exceptionCallback(eType, eValue, eTraceBack):
        import cgitb

        txt = cgitb.text((eType, eValue, eTraceBack))

        logging.fatal(txt)
    
        # sys.exit(1)

    # configure file logger
    logging.basicConfig(level = logging.DEBUG,
                        format = '%(asctime)s %(levelname)s %(message)s',
                        filename = '/tmp/tagfs.log',
                        filemode = 'a')
    
    # configure console logger
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    
    consoleFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    consoleHandler.setFormatter(consoleFormatter)
    logging.getLogger().addHandler(consoleHandler)

    # replace default exception handler
    sys.excepthook = exceptionCallback
    
    logging.debug('Logging and exception handling has been set up')

if __name__ == '__main__':
    from os import environ as env
    if 'DEBUG' in env:
        setUpLogging()
    
    pass

#====================================================================
# here the application begins

import os
import stat
import errno
import fuse
import exceptions
import time
import functools

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

from cache import cache
import item_access
import node
    
class TagFS(fuse.Fuse):
    
    def __init__(self, initwd, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        
        self._initwd = initwd
        self._itemsRoot = None
        self.__itemAccess = None
        
        self.parser.add_option('-i',
                               '--items-dir',
                               dest = 'itemsDir',
                               help = 'items directory',
                               metavar = 'dir')
        self.parser.add_option('-t',
                               '--tag-file',
                               dest = 'tagFile',
                               help = 'tag file name',
                               metavar = 'file',
                               default = '.tag')

    @cache
    def getItemAccess(self):
        # Maybe we should move the parser run from main here.
        # Or we should at least check if it was run once...
        opts, args = self.cmdline

        # Maybe we should add expand user? Maybe even vars???
        assert opts.itemsDir != None and opts.itemsDir != ''
        self._itemsRoot = os.path.normpath(
                os.path.join(self._initwd, opts.itemsDir))
        
        self.tagFileName = opts.tagFile
    
        # try/except here?
        try:
            return item_access.ItemAccess(self._itemsRoot, self.tagFileName)
        except OSError, e:
            logging.error("Can't create item access from items directory %s. Reason: %s",
                    self._itemsRoot, str(e.strerror))
            raise
    
    @cache
    def __getRootNode(self):
        return node.RootNode(self.getItemAccess())
    
    def __getNode(self, path):
        rootNode = self.__getRootNode()
        
        parentNode = rootNode
        for pathElement in (x for x in
                os.path.normpath(path).split(os.sep) if x != ''):
            parentNode = parentNode.getSubNode(pathElement)
            
            if parentNode == None:
                return None
            
        return parentNode
    
    def getattr(self, path):
        logging.debug('getattr ' + path)

        node = self.__getNode(path)
        
        if node == None:
            logging.info('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.attr

    def readdir(self, path, offset):
        logging.debug('readdir ' + path)

        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        
        node = self.__getNode(path)
        if node == None:
            logging.info('Unknown node for path ' + path)
            
            # TODO maybe we should fail here?
            return
        
        for subNode in node.subNodes:
            yield subNode.direntry
            
    def readlink(self, path):
        logging.debug('readlink ' + path)

        node = self.__getNode(path)
        
        if node == None:
            logging.info('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.link

    def open(self, path, flags):
        return -errno.ENOENT

    def read(self, path, size, offset):
        return -errno.ENOENT

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
        sys.exit()
        
    return fs.main()

if __name__ == '__main__':
    import sys
    sys.exit(main())
