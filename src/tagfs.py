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
    logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s',
                        filename = '/tmp/tagfs.log',
                        filemode='a')
    
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
    # TODO implement cmd line configurable logging
    setUpLogging()
    
    pass

#====================================================================
# here the application begins

import os
import stat
import errno
import fuse
import exceptions
import datetime

if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

class ItemAccess(object):
    
    # When the time delta between now and the last time the item directories
    # have been parsed is bigger than self.refreshTimeDelta then the item
    # directories have to be parsed again.
    refreshTimeDelta = datetime.timedelta(0, 10 * 60)
    
    def __init__(self, dataDirectory, tagFileName):
        self.dataDirectory = dataDirectory
        self.tagFileName = tagFileName
        
        self.__parseItems()
        
    def __now(self):
        return datetime.datetime.utcnow()
    
    def __isItemsDirectoryOutOfDate(self):
        now = self.__now()
        
        return (now - self.__itemsParseDateTime > self.refreshTimeDelta)
    
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
                
                tagFileName = directory + '/' + self.tagFileName
                
                if(not os.path.exists(tagFileName)):
                    continue
                
                tagFile = open(tagFileName, 'r')
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
        self.__itemsParseDateTime = self.__now()
        
    def __validateItemsData(self):
        if(not self.__isItemsDirectoryOutOfDate()):
            return
        
        logging.debug('Reparsing item directories because the cache is out of date.')
        
        self.__parseItems()
        
    def __getItems(self):
        self.__validateItemsData()
        
        return self.__items
    
    items = property(__getItems)
    
    def __getTags(self):
        self.__validateItemsData()
        
        return self.__tags
    
    tags = property(__getTags)
    
    def getItemDirectory(self, item):
        return self.dataDirectory + '/' + item
    
    def filter(self, tagFilters):
        tagFiltersSet = set(tagFilters)
        resultItems = []
        resultTags = set()
        
        for itemName, itemTags in self.items.iteritems():
            if(len(tagFiltersSet & itemTags) < len(tagFilters)):
                continue
            
            resultItems.append(itemName)
            
            for itemTag in itemTags:
                resultTags.add(itemTag)
                
        resultTags = resultTags - tagFiltersSet
        
        return (resultItems, resultTags)
        
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

class Node(object):
    
    def _addSubNodes2(self, subNodes, nodesDict):
        for nodeNames, nodes in nodesDict.iteritems():
            for node in nodes:
                if(node.name in subNodes):
                    logging.debug('%s is shadowed by %s',
                                  nodeNames,
                                  subNodes[node.name])
                    
                    continue
                
                subNodes[node.name] = node
    
    def _addSubNodes(self, subNodes, items, tags):
        """Adds items and tags to the subNodes list.
        
        @deprecated: This method should not be used anymore. Instead call the
        _addSubNodes(self, subNodes, nodesDict) method.
        """
        
        nodesDict = {
            'items': [ItemNode(self, item, self.itemAccess) for item in items],
            'tags': [TagNode(self, tag, self.itemAccess) for tag in tags]
        }
        
        self._addSubNodes2(subNodes, nodesDict)

    def __getSubNodes(self):
        return [node for name, node in self._getSubNodesDict().iteritems()]
    
    subNodes = property(__getSubNodes)
    
    def getSubNode(self, pathElement):
        subNodesDict = self._getSubNodesDict()
        
        if(not pathElement in subNodesDict):
            logging.warning('Unknown path element requested ' + pathElement)
            
            return None
        
        return subNodesDict[pathElement]

class ItemNode(Node):
    
    def __init__(self, parentNode, itemName, itemAccess):
        self.parentNode = parentNode
        self.name = itemName
        self.itemAccess = itemAccess
    
    def __getSubNodes(self):
        """Returns always [] because we don't have sub nodes.
        """

        return []
    
    subNodes = property(__getSubNodes)

    def getSubNode(self, pathElement):
        """Returns always None as item nodes don't have sub nodes.
        """
        return None
    
    def __getAttr(self):
        # TODO modify to match softlink
        st = MyStat()
        st.st_mode = stat.S_IFLNK | 0444
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)
    
    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFLNK
        
        return e
    
    direntry = property(__getDirentry)
    
    def __getLink(self):
        return self.itemAccess.getItemDirectory(self.name)
    
    link = property(__getLink)
    
class TagNode(Node):
    
    def __init__(self, parentNode, tagName, itemAccess):
        self.parentNode = parentNode
        self.name = tagName
        self.itemAccess = itemAccess
        
    def __getFilterTags(self):
        filterTags = [tag for tag in self.parentNode.filterTags]
        filterTags.append(self.name)
        
        return filterTags
    
    filterTags = property(__getFilterTags)
    
    def _getSubNodesDict(self):
        items, tags = self.itemAccess.filter(self.filterTags)
        
        subNodes = {}
        
        self._addSubNodes(subNodes, items, tags)
        
        return subNodes
    
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)

    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    
    direntry = property(__getDirentry)
    
class RootNode(Node):
    
    def __init__(self, itemAccess):
        self.itemAccess = itemAccess
        self.filterTags = []
        
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes, self.itemAccess.items, self.itemAccess.tags)
        
        return subNodes
        
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)
    
    def __getDirentry(self):
        return None
    
    direntry = property(__getDirentry)
    
class TagFS(fuse.Fuse):
    
    def determineItemsDirectory(self):
        opts, args = self.cmdline
        
        self.itemsDirectory = os.path.abspath(opts.itemsDir)
    
    def __init__(self, *args, **kw):
        fuse.Fuse.__init__(self, *args, **kw)
        
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
        
    def getItemAccess(self):
        if(self.__itemAccess == None):
            try:
                opts, args = self.cmdline
                
                itemsDir = self.itemsDirectory
                tagFile = opts.tagFile
            
                self.__itemAccess = ItemAccess(itemsDir, tagFile)
            except exceptions.OSError, e:
                logging.error('Can \'t create item access from items directory '
                              + self.itemsDirectory + '. Reason: '
                              + str(e.strerror))
                
                raise e
            
        return self.__itemAccess
    
    def __getNode(self, path):
        logging.debug('Requesting node for path ' + path)
        
        # TODO implement some caching
        rootNode = RootNode(self.getItemAccess())
        
        parentNode = rootNode
        # TODO implement escaping path splitting
        for pathElement in path.split('/'):
            if(len(pathElement) == 0):
                continue
            
            parentNode = parentNode.getSubNode(pathElement)
            
            if(parentNode == None):
                logging.info('No node can be resolved for path ' + path)
                
                return None
            
        return parentNode
    
    def getattr(self, path):
        node = self.__getNode(path)
        
        if(node == None):
            logging.debug('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.attr

    def readdir(self, path, offset):
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        
        node = self.__getNode(path)
        if(node == None):
            logging.debug('Unknown node for path ' + path)
            
            # TODO maybe we should fail here?
            return
        
        for subNode in node.subNodes:
            yield subNode.direntry
            
    def readlink(self, path):
        node = self.__getNode(path)
        
        if(node == None):
            logging.debug('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.link

    def open(self, path, flags):
        return -errno.ENOENT

    def read(self, path, size, offset):
        return -errno.ENOENT

def main():
    fs = TagFS(version = "%prog " + fuse.__version__,
               usage = fuse.Fuse.fusage,
               dash_s_do = 'setsingle')

    fs.parse(errex = 1)
    opts, args = fs.cmdline
    
    if(opts.itemsDir == None):
        fs.parser.error('Missing items directory option')
        
    fs.determineItemsDirectory()
            
    fs.main()

if __name__ == '__main__':
    main()
