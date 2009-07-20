#!/usr/bin/env python
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
#
# = tag fs =
# == glossary ==
# * item: An item is a directory in the item container directory. Items can be
# tagged using a tag file.
# * tag: A tag is a text string which can be assigned to an item. Tags can
# consist of any character except newlines.

import sys
import os
import stat
import errno
import fuse
import logging

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

hello_path = '/hello'
hello_str = 'Hello World!\n'

def setUpLogging():
    def exceptionCallback(eType, eValue, eTraceBack):
        import cgitb

        txt = cgitb.text((eType, eValue, eTraceBack))

        logging.fatal(txt)
    
        # sys.exit(1)

    # configure file logger
    logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s', filename = '/tmp/tagfs.log', filemode='a')
    
    # configure console logger
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    
    consoleFormatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    consoleHandler.setFormatter(consoleFormatter)
    logging.getLogger().addHandler(consoleHandler)

    # replace default exception handler
    sys.excepthook = exceptionCallback

class ItemAccess(object):
    
    def __init__(self, dataDirectory, tagFileName):
        self.dataDirectory = dataDirectory
        self.tagFileName = tagFileName
        
        self.__parseItems()
        
    def __parseItems(self):
        items = {}
        tags = set()
        
        for directoryName in os.listdir(self.dataDirectory):
            try:
                itemTags = set()
                items[directoryName] = itemTags
                
                directory = self.dataDirectory + '/' + directoryName
                
                if(not os.path.isdir(directory)):
                    continue
                
                tagFile = open(directory + '/' + self.tagFileName, 'r')
                try:
                    for rawTag in tagFile.readlines():
                        tag = rawTag.strip()
                        
                        if(len(tag) == 0):
                            continue
                        
                        tags.add(tag)
                        itemTags.add(tag)
                finally:
                    tagFile.close()
            
            except:
                logging.error('Can \'t read tags for item ' + directoryName 
                              + ': ' + str(sys.exc_info()[0]))
                
        logging.debug('Found ' + str(len(items)) + ' items')
        logging.debug('Found ' + str(len(tags)) + ' tags')
        
        self.__items = items
        self.__tags = tags
        
    def __getItems(self):
        
        return self.__items
    
    items = property(__getItems)
    
    def __getTags(self):
        
        return self.__tags
    
    tags = property(__getTags)
        
class MyStat(fuse.Stat):
    
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

class TagNode(object):
    
    def __init__(self, parentNode, tagName):
        self.parentNode = parentNode
        self.name = tagName
        
    def __getSubNodes(self):
        # TODO
        return []
    
    subNodes = property(__getSubNodes)

    def getSubNode(self, pathElement):
        # TODO
        pass
    
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)

    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    
    direntry = property(__getDirentry)
    
class RootNode(object):
    
    def __init__(self, itemAccess):
        self.itemAccess = itemAccess
        
    def __getSubNodesDict(self):
        subNodes = {}
        
        for tag in self.itemAccess.tags:
            subNodes[tag] = TagNode(self, tag)
        
        # TODO add item sub nodes
        
        return subNodes
        
    def __getSubNodes(self):
        return [node for name, node in self.__getSubNodesDict().iteritems()]
    
    subNodes = property(__getSubNodes)
    
    def getSubNode(self, pathElement):
        subNodesDict = self.__getSubNodesDict()
        
        if(not pathElement in subNodesDict):
            logging.warning('Unknown path element requested ' + pathElement)
            
            return None
        
        return subNodesDict[pathElement]
    
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)
    
    def __getDirentry(self):
        return None
    
    direntry = property(__getDirentry)
    
class ItemNode(object):
    
    def __init__(self, parentNode, itemName):
        self.parentNode = parentNode
        self.name = itemName
    
    def __getSubNodes(self):
        # TODO
        pass
    
    subNodes = property(__getSubNodes)

    def getSubNode(self, pathElement):
        """Returns always None as item nodes don't have sub nodes.
        """
        return None
    
    def __getAttr(self):
        # TODO modify to match softlink
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0755
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)
    
    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFLNK
        
        return e
    
    direntry = property(__getDirentry)
    
class TagFS(fuse.Fuse):
    
    def __getNode(self, path):
        # TODO implement some caching
        rootNode = RootNode(self.itemAccess)
        
        parentNode = rootNode
        # TODO implement escaping path splitting
        for pathElement in path.split('/'):
            if(len(pathElement) == 0):
                continue
            
            parentNode = parentNode.getSubNode(pathElement)
            
            if(parentNode == None):
                return None
            
        return parentNode
    
    def getattr(self, path):
        node = self.__getNode(path)
        
        if(node == None):
            logging.debug('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.attr

    def readdir(self, path, offset):
        logging.debug('Fetching directory content for path ' + path)
        
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        
        node = self.__getNode(path)
        if(node == None):
            logging.debug('Unknown node for path ' + path)
            
            # TODO maybe we should fail here?
            return
        
        for subNode in node.subNodes:
            yield subNode.direntry

    def open(self, path, flags):
        return -errno.ENOENT

    def read(self, path, size, offset):
        return -errno.ENOENT

def main():
    usage = """TODO
""" + fuse.Fuse.fusage

    setUpLogging()
    
    server = TagFS(version = "%prog " + fuse.__version__,
                     usage = usage,
                     dash_s_do = 'setsingle')
    server.itemAccess = ItemAccess('/home/marook/work/environment/events/', '.tag')

    server.parse(errex = 1)
    server.main()

if __name__ == '__main__':
    main()
