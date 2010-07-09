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

from cache import cache
import errno
import log
import logging
import node
import os
from transient_dict import TransientDict

class View(object):
    """Abstraction layer from fuse API.

    This class is an abstraction layer from the fuse API. This should ease
    writing test cases for the file system.
    """

    DEFAULT_NODES = {
        '.DirIcon': None,
        'AppRun': None
        }
    
    def __init__(self, itemAccess, config):
        self.itemAccess = itemAccess
        self.config = config
        self._nodeCache = TransientDict(100)

    @cache
    def getRootNode(self):
        return node.RootNode(self.itemAccess, self.config)

    def getNode(self, path):
        if path in self._nodeCache:
            # simple path name based caching is implemented here

            logging.debug('tagfs _nodeCache hit')

            return self._nodeCache[path]

        # ps contains the path segments
        ps = [x for x in os.path.normpath(path).split(os.sep) if x != '']

        psLen = len(ps)
        if psLen > 0:
            lastSegment = ps[psLen - 1]
            
            if lastSegment in View.DEFAULT_NODES:
                logging.debug('Using default node for path ' + path)

                return View.DEFAULT_NODES[lastSegment]

        n = self.getRootNode()

        for e in path.split('/')[1:]:
            if e == '':
                continue

            n = n.getSubNode(e)

            if not n:
                # it seems like we are trying to fetch a node for an illegal
                # path

                break

        logging.debug('tagfs _nodeCache miss')
        self._nodeCache[path] = n

        return n

    @log.logCall
    def getattr(self, path):
        n = self.getNode(path)

        if not n:
            logging.debug('Try to read attributes from not existing node: ' + path)

            return -errno.ENOENT

        return n.getattr(path)

    @log.logCall
    def readdir(self, path, offset):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to read not existing directory: ' + path)

            return -errno.ENOENT

        return n.readdir(path, offset)

    @log.logCall
    def readlink(self, path):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to read not existing link from node: ' + path)

            return -errno.ENOENT

        return n.readlink(path)

    @log.logCall
    def symlink(self, path, linkPath):
        linkPathSegs = linkPath.split('/')

        n = self.getNode('/'.join(linkPathSegs[0:len(linkPathSegs) - 2]))

        if not n:
            return -errno.ENOENT

        return n.symlink(path, linkPath)

    @log.logCall
    def open(self, path, flags):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to open not existing node: ' + path)

            return -errno.ENOENT

        return n.open(path, flags)

    @log.logCall
    def read(self, path, len, offset):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to read from not existing node: ' + path)

            return -errno.ENOENT

        return n.read(path, len, offset)

    @log.logCall
    def write(self, path, data, pos):
        n = self.getNode(path)

        if not n:
            logging.warn('Try to write to not existing node: ' + path)

            return -errno.ENOENT

        return n.write(path, data, pos)
	
