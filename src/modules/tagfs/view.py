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

import errno
import logging
import os
from log import logCall, logException
from cache import cache
from transient_dict import TransientDict
from node_root import RootDirectoryNode
from fuse import Direntry

class View(object):
    """Abstraction layer from fuse API.

    This class is an abstraction layer from the fuse API. This should ease
    writing test cases for the file system.
    """

    DEFAULT_NODES = {
        # directory icons for rox filer
        '.DirIcon': None,

        # launch script for rox filer application directories
        'AppRun': None
        }
    
    def __init__(self, itemAccess, config):
        self.itemAccess = itemAccess
        self.config = config
        self._entryCache = TransientDict(100)

    @property
    @cache
    def rootNode(self):
        return RootDirectoryNode(self.itemAccess, self.config)

    def getNode(self, path):
        if path in self._entryCache:
            # simple path name based caching is implemented here

            logging.debug('tagfs _entryCache hit')

            return self._entryCache[path]

        # ps contains the path segments
        ps = [x for x in os.path.normpath(path).split(os.sep) if x != '']

        psLen = len(ps)
        if psLen > 0:
            lastSegment = ps[psLen - 1]
            
            if lastSegment in View.DEFAULT_NODES:
                logging.debug('Using default node for path ' + path)

                return View.DEFAULT_NODES[lastSegment]

        e = self.rootNode

        for pe in path.split('/')[1:]:
            if pe == '':
                continue

            entries = e.entries

            if not pe in entries:
                # it seems like we are trying to fetch a node for an illegal
                # path

                return None

            e = entries[pe]

        logging.debug('tagfs _entryCache miss')
        self._entryCache[path] = e

        return e

    @logCall
    def getattr(self, path):
        e = self.getNode(path)

        if not e:
            logging.debug('Try to read attributes from not existing node: ' + path)

            return -errno.ENOENT

        return e.attr

    @logCall
    def readdir(self, path, offset):
        e = self.getNode(path)

        if not e:
            logging.warn('Try to read not existing directory: ' + path)

            return -errno.ENOENT

        # TODO care about offset parameter

        # without the decode/encode operations fuse refuses to show directory
        # entries which are based on freebase data
        return [Direntry(name.decode('ascii', 'ignore').encode('ascii')) for name in e.entries.iterkeys()]

    @logCall
    def readlink(self, path):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to read not existing link from node: ' + path)

            return -errno.ENOENT

        return n.link

    @logCall
    def symlink(self, path, linkPath):
        linkPathSegs = linkPath.split('/')

        n = self.getNode('/'.join(linkPathSegs[0:len(linkPathSegs) - 2]))

        if not n:
            return -errno.ENOENT

        return n.symlink(path, linkPath)

    @logCall
    def open(self, path, flags):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to open not existing node: ' + path)

            return -errno.ENOENT

        return n.open(path, flags)

    @logCall
    def read(self, path, len, offset):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to read from not existing node: ' + path)

            return -errno.ENOENT

        return n.read(path, len, offset)

    @logCall
    def write(self, path, data, pos):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to write to not existing node: ' + path)

            return -errno.ENOENT

        return n.write(path, data, pos)
	
