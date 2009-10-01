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

def noCacheStrategy(f, *args, **kwargs):
    """This cache strategy reloads the cache on every call.
    """
    
    return False

def noReloadStrategy(f, *args, **kwargs):
    """This cache strategy never reloads the cache.
    """
    
    return True

def timeoutReloadStrategy(f, *args, **kwargs):
    timestampFieldName = '__' + f.__name__ + 'Timestamp'
    now = time.time()
    
    if not hasattr(args[0], timestampFieldName):
        setattr(args[0], timestampFieldName, now)
        
        return False
    
    lastTime = getattr(args[0], timestampFieldName)
    
    # TODO make time interval dynamic
    if now - lastTime < 10 * 60:
        return False
    
    setattr(args[0], timestampFieldName, now)
    
    return True
    

def cache(f, reload = timeoutReloadStrategy):
    """This annotation is used to cache the result of a method call.
    
    @param f: This is the wrapped function which's return value will be cached.
    @param reload: This is the reload strategy. This function returns True when
    the cache should be reloaded. Otherwise False.
    @attention: The cache is never deleted. The first call initializes the
    cache. The method's parameters just passed to the called method. The cache
    is not evaluating the parameters.
    """
    
    @functools.wraps(f)
    def cacher(*args, **kwargs):
        obj = args[0]
        
        cacheMemberName = '__' + f.__name__ + 'Cache'
        
        # the reload(...) call has to be first as we always have to call the
        # method. not only when there is a cache member available in the object.
        if reload(f, *args, **kwargs) or not hasattr(obj, cacheMemberName):
            value = f(*args, **kwargs)
            
            setattr(obj, cacheMemberName, value)
            
            return value
            
        return getattr(obj, cacheMemberName)
    
    return cacher
    

def parseTagsFromFile(tagFileName):
    """Parses the tags from the specified file.
    
    @return: The parsed values are returned as a set containing the tag strings.
    """
    
    tags = set()
    
    tagFile = open(tagFileName, 'r')
    try:
        for rawTag in tagFile.readlines():
            tag = rawTag.strip()
                        
            if len(tag) == 0:
                continue
                        
            tags.add(tag)
    finally:
        tagFile.close()
        
    return tags
    
class Item(object):
    
    def __init__(self, name, itemAccess):
        self.name = name
        self.itemAccess = itemAccess
        
        # TODO register at file system to receive tag file change events.
        
    @cache
    def __getItemDirectory(self):
        return os.path.join(self.itemAccess.dataDirectory, self.name)
    
    itemDirectory = property(__getItemDirectory)
    
    @cache
    def __getTagFileName(self):
        """Returns the name of the tag file for this item.
        
        This method is published via the property __tagFileName.
        """
        
        itemDirectory = self.itemDirectory

        return os.path.join(itemDirectory, self.itemAccess.tagFileName)
        
    __tagFileName = property(__getTagFileName)
    
    def __parseTags(self):
        tagFileName = self.__tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return parseTagsFromFile(tagFileName)

    @cache
    def __getTagsCreationTime(self):
        
        # TODO implement some caching
        
        tagFileName = self.__tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return os.path.getctime(self.__tagFileName)
    
    tagsCreationTime = property(__getTagsCreationTime)
        
    @cache
    def __getTagsModificationTime(self):
        """Returns the last time when the tags have been modified.
        
        This method is published via the property tagsModificationDate.
        """
        
        # TODO implement some caching
        
        tagFileName = self.__tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return os.path.getmtime(self.__tagFileName)
    
    tagsModificationTime = property(__getTagsModificationTime)
        
    @cache
    def __getTags(self):
        """Returns the tags as a list for this item.
        
        This method is published via the property tags.
        """
        
        # TODO implement some caching
        
        return self.__parseTags()
    
    tags = property(__getTags)
    
    @cache
    def __isTagged(self):
        
        # TODO implement some caching
        
        return os.path.exists(self.__tagFileName)
    
    tagged = property(__isTagged)
        

class ItemAccess(object):
    """This is the access point to the Items.
    """
    
    def __init__(self, dataDirectory, tagFileName):
        self.dataDirectory = dataDirectory
        self.tagFileName = tagFileName
        
        self.__items = None
        self.__tags = None
        self.__taggedItems = None
        self.__untaggedItems = None
        
    def __parseItems(self):
        items = {}
        
        logging.debug('Start parsing items from dir: %s', self.dataDirectory)
        
        for itemName in os.listdir(self.dataDirectory):
            try:
                item = Item(itemName, self)
                
                items[itemName] = item
                
            except IOError, (error, strerror):
                logging.error('Can \'t read tags for item %s: %s',
                              itemName,
                              strerror)
                
        logging.debug('Found %s items', len(items))
        
        return items
    
    @cache
    def __getItems(self):
        # TODO improve cache handling. especially reload the cache sometimes.
        
        return self.__parseItems()
    
    items = property(__getItems)
    
    @cache
    def __getTags(self):
        tags = set()
        
        for item in self.items.itervalues():
            if not item.tagged:
                continue
            
            tags = tags | item.tags
            
        return tags
    
    tags = property(__getTags)
    
    @cache
    def __getTaggedItems(self):
        return set([item for item in self.items.itervalues() if item.tagged])
    
    taggedItems = property(__getTaggedItems)
    
    @cache
    def __getUntaggedItems(self):
        return set([item for item in self.items.itervalues() if not item.tagged])

    untaggedItems = property(__getUntaggedItems)
    
    def getItemDirectory(self, item):
        return os.path.join(self.dataDirectory, item)
    
    def filter(self, tagFilters):
        tagFiltersSet = set(tagFilters)
        resultItems = []
        resultTags = set()
        
        for item in self.taggedItems:
            if len(tagFiltersSet & item.tags) < len(tagFilters):
                continue
            
            resultItems.append(item)
            
            for itemTag in item.tags:
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
    
    def _addSubNodes(self, subNodes, nodeNames, nodes):
        for node in nodes:
            if node.name in subNodes:
                logging.debug('%s is shadowed by %s',
                              nodeNames,
                              subNodes[node.name])
                    
                continue
                
            subNodes[node.name] = node
    
    @cache
    def __getSubNodes(self):
        return [node for name, node in self._getSubNodesDict().iteritems()]
    
    subNodes = property(__getSubNodes)
    
    def getSubNode(self, pathElement):
        subNodesDict = self._getSubNodesDict()
        
        if not pathElement in subNodesDict:
            logging.warning('Unknown path element requested ' + pathElement)
            
            return None
        
        return subNodesDict[pathElement]

class ItemNode(Node):
    
    def __init__(self, itemName, itemAccess):
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
    
    @cache
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFLNK | 0444
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)
    
    @cache
    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFLNK
        
        return e
    
    direntry = property(__getDirentry)
    
    @cache
    def __getLink(self):
        return self.itemAccess.getItemDirectory(self.name)
    
    link = property(__getLink)
    
class UntaggedItemsNode(Node):
    """Represents a node which contains not tagged items.
    """
    
    def __init__(self, name, itemAccess):
        self.name = name
        self.itemAccess = itemAccess
    
    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in self.itemAccess.untaggedItems])
        
        return subNodes
    
    @cache
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)

    @cache
    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    
    direntry = property(__getDirentry)

class TagNode(Node):
    
    def __init__(self, parentNode, tagName, itemAccess):
        self.parentNode = parentNode
        self.name = tagName
        self.itemAccess = itemAccess
        
    @cache
    def __getFilterTags(self):
        filterTags = [tag for tag in self.parentNode.filterTags]
        filterTags.append(self.name)
        
        return filterTags
    
    filterTags = property(__getFilterTags)
    
    @cache
    def __getItems(self):
        items, tags = self.itemAccess.filter(self.filterTags)
        
        return items
    
    items = property(__getItems)
    
    @cache
    def _getSubNodesDict(self):
        items, tags = self.itemAccess.filter(self.filterTags)
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubNodes(subNodes,
                          'tags',
                          [tagNode for tagNode in [TagNode(self, tag, self.itemAccess) for tag in tags] if (len(items) > len(tagNode.items))])
        
        return subNodes
    
    @cache
    def __getAttr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    attr = property(__getAttr)

    @cache
    def __getDirentry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    
    direntry = property(__getDirentry)
    
class RootNode(Node):
    
    def __init__(self, itemAccess):
        self.itemAccess = itemAccess
        self.filterTags = []
        
    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'untagged items',
                          [UntaggedItemsNode('.untagged', self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in self.itemAccess.items])
        self._addSubNodes(subNodes,
                          'tags',
                          [TagNode(self, tag, self.itemAccess) for tag in self.itemAccess.tags])
        
        return subNodes
        
    @cache
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
            return ItemAccess(self._itemsRoot, self.tagFileName)
        except OSError, e:
            logging.error("Can't create item access from items directory %s. Reason: %s",
                    self._itemsRoot, str(e.strerror))
            raise
    
    @cache
    def __getRootNode(self):
        return RootNode(self.getItemAccess())
    
    def __getNode(self, path):
        logging.debug('Requesting node for path ' + path)
        
        # TODO implement some caching
        rootNode = self.__getRootNode()
        
        parentNode = rootNode
        for pathElement in (x for x in
                os.path.normpath(path).split(os.sep) if x != ''):
            parentNode = parentNode.getSubNode(pathElement)
            
            if parentNode == None:
                logging.info('No node can be resolved for path ' + path)
                
                return None
            
        return parentNode
    
    def getattr(self, path):
        node = self.__getNode(path)
        
        if node == None:
            logging.debug('Unknown node for path ' + path)
            
            return -errno.ENOENT
        
        return node.attr

    def readdir(self, path, offset):
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        
        node = self.__getNode(path)
        if node == None:
            logging.debug('Unknown node for path ' + path)
            
            # TODO maybe we should fail here?
            return
        
        for subNode in node.subNodes:
            yield subNode.direntry
            
    def readlink(self, path):
        node = self.__getNode(path)
        
        if node == None:
            logging.debug('Unknown node for path ' + path)
            
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
        
    fs.main()

if __name__ == '__main__':
    main()
