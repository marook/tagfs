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

class NoCacheStrategy(object):
    """This cache strategy reloads the cache on every call.
    """
    
    def isCacheValid(self, f, *args, **kwargs):
        return False
    
class NoReloadStrategy(object):
    """This cache strategy never reloads the cache.
    """
    
    def isCacheValid(self, f, *args, **kwargs):
        return True

class TimeoutReloadStrategy(object):
    
    def __init__(self, timeoutDuration = 10 * 60):
        self.timeoutDuration = timeoutDuration
    
    def isCacheValid(self, f, *args, **kwargs):
        timestampFieldName = '__' + f.__name__ + 'Timestamp'
        now = time.time()
    
        if not hasattr(args[0], timestampFieldName):
            setattr(args[0], timestampFieldName, now)
        
            return False
    
        lastTime = getattr(args[0], timestampFieldName)
    
        if now - lastTime < self.timeoutDuration:
            return False
    
        setattr(args[0], timestampFieldName, now)
    
        return True
    

def cache(f, reloadStrategy = TimeoutReloadStrategy()):
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
        if reloadStrategy.isCacheValid(f, *args, **kwargs) or not hasattr(obj, cacheMemberName):
            value = f(*args, **kwargs)
            
            setattr(obj, cacheMemberName, value)
            
            return value
            
        return getattr(obj, cacheMemberName)
    
    return cacher
    
class Tag(object):
    
    def __init__(self, value, context = None):
        if context == None:
            self.context = None
        else:
            self.context = context.strip()
        
        self.value = value.strip()
        
        if not self.context == None and len(self.context) == 0:
            # we don't allow empty strings as they can't be represented as a
            # directory very well
            raise ValueError()

        if len(self.value) == 0:
            # we don't allow empty strings as they can't be represented as a
            # directory very well
            raise ValueError()
        
    def __hash__(self):
        return (self.context, self.value).__hash__()
    
    def __eq__(self, other):
        return self.value == other.value and self.context == other.context
        
    def __repr__(self):
        return '<Tag %s: %s>' % (self.context, self.value)

def parseTagsFromFile(tagFileName):
    """Parses the tags from the specified file.
    
    @return: The parsed values are returned as a set containing Tag objects.
    @see: Tag
    """
    
    tags = set()
    
    tagFile = open(tagFileName, 'r')
    try:
        for rawTag in tagFile.readlines():
            rawTag = rawTag.strip()
            
            if len(rawTag) == 0:
                continue
            
            tagTuple = rawTag.split(':', 1)
            
            if len(tagTuple) == 1:
                tagContext = None
                tagValue = tagTuple[0]
            else:
                tagContext = tagTuple[0]
                tagValue = tagTuple[1]
                
            tag = Tag(tagValue, context = tagContext)

            tags.add(tag)
    finally:
        tagFile.close()
        
    return tags
    
class Item(object):
    
    def __init__(self, name, itemAccess):
        self.name = name
        self.itemAccess = itemAccess
        
        # TODO register at file system to receive tag file change events.
        
    @property
    @cache
    def itemDirectory(self):
        return os.path.join(self.itemAccess.dataDirectory, self.name)
    
    @property
    @cache
    def _tagFileName(self):
        """Returns the name of the tag file for this item.
        """
        
        itemDirectory = self.itemDirectory

        return os.path.join(itemDirectory, self.itemAccess.tagFileName)
    
    def __parseTags(self):
        tagFileName = self._tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return parseTagsFromFile(tagFileName)

    @property
    @cache
    def tagsCreationTime(self):
        
        # TODO implement some caching
        
        tagFileName = self._tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return os.path.getctime(self._tagFileName)
    
    @property
    @cache
    def tagsModificationTime(self):
        """Returns the last time when the tags have been modified.
        """
        
        tagFileName = self._tagFileName
        
        if not os.path.exists(tagFileName):
            return None

        return os.path.getmtime(tagFileName)
    
    @property
    @cache
    def tags(self):
        """Returns the tags as a list for this item.
        """
        
        # TODO implement some caching
        
        return self.__parseTags()
    
    @property
    @cache
    def tagged(self):
        
        # TODO implement some caching
        
        return os.path.exists(self._tagFileName)
    
    def __repr__(self):
        return '<Item %s>' % self.name
    
class TagValueFilter(object):
    
    def __init__(self, tagValue):
        self.tagValue = tagValue
        
    def filterItems(self, items):
        droppedItems = set()
        
        for item in items:
            hasTagValue = False
                
            for itemTag in item.tags:
                if itemTag.value == self.tagValue:
                    hasTagValue = True
                    
                    break
                
            if not hasTagValue:
                droppedItems.add(item)
                
        items -= droppedItems
        
class TagFilter(object):
    
    def __init__(self, tag):
        self.tag = tag
        
    def filterItems(self, items):
        droppedItems = set()
        
        for item in items:
            if not self.tag in item.tags:
                droppedItems.add(item)
                
        items -= droppedItems
        
class AndFilter(object):
    """Concatenates two filters with a logical 'and'.
    """
    
    def __init__(self, subFilters):
        self.subFilters = subFilters
        
    def filterItems(self, items):
        for subFilter in self.subFilters:
            subFilter.filterItems(items)
            
class NoneFilter(object):
    
    def filterItems(self, items):
        pass
    
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
    
    @property
    @cache
    def items(self):
        return self.__parseItems()
    
    @property
    @cache
    def tags(self):
        tags = set()
        
        for item in self.items.itervalues():
            if not item.tagged:
                continue
            
            tags = tags | item.tags
            
        return tags

    @property
    @cache
    def taggedItems(self):
        return set([item for item in self.items.itervalues() if item.tagged])
    
    @property
    @cache
    def untaggedItems(self):
        return set([item for item in self.items.itervalues() if not item.tagged])

    def getItemDirectory(self, item):
        return os.path.join(self.dataDirectory, item)
    
    def filterItems(self, filter):
        resultItems = set([item for item in self.taggedItems])
        
        filter.filterItems(resultItems)
        
        return resultItems
    
    def contextTags(self, context):
        contextTags = set()
        
        for tag in self.tags:
            if tag.context == context:
                contextTags.add(tag)
                
        return contextTags
    
    @property
    @cache
    def contexts(self):
        contexts = set()
        
        for tag in self.tags:
            if tag.context == None:
                continue
            
            contexts.add(tag.context)
        
        return contexts
        
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
        """Adds the supplied nodes to the sub nodes.
        
        @param subNodes: This dict is extended with the nodes.
        @param nodeNames: This is a logical name for the added nodes. It's just
        used for logging.
        @param nodes: This list contains the added nodes.
        """
        for node in nodes:
            if node.name in subNodes:
                logging.debug('%s is shadowed by %s',
                              nodeNames,
                              subNodes[node.name])
                    
                continue
                
            subNodes[node.name] = node
            
    @property
    @cache
    def subNodes(self):
        return [node for name, node in self._getSubNodesDict().iteritems()]
    
    def getSubNode(self, pathElement):
        subNodesDict = self._getSubNodesDict()
        
        if not pathElement in subNodesDict:
            logging.warning('Unknown path element requested ' + pathElement)
            
            return None
        
        return subNodesDict[pathElement]

class ContainerNode(Node):
    """Abstract base node for nodes which contain items and or tags.
    
    Facts about ContainerNodes:
    * container nodes are always represented as directories
    """
    
    def _addSubContainerNodes(self, subNodes, nodeNames, containerNodes):
        items = self.items
        
        self._addSubNodes(subNodes,
                          nodeNames,
                          [n for n in containerNodes if n.required(items)])
        
    def __init__(self, parentNode):
        self.parentNode = parentNode
        
    def required(self, items):
        selfItems = self.items
        selfItemsLen = len(self.items)
        
        return not selfItemsLen == 0 and not selfItemsLen == len(items)
            
    @property
    @cache
    def filter(self):
        parentFilter = self.parentNode.filter
        
        return AndFilter([parentFilter, self._myFilter])
    
    @property
    @cache
    def items(self):
        items = self.itemAccess.filterItems(self.filter)
        
        logging.debug('Items request for %s: %s',
                      self,
                      [item.name for item in items])
        
        return items
    
    @property
    @cache
    def attr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    @property
    @cache
    def direntry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    

class ItemNode(Node):
    
    def __init__(self, item, itemAccess):
        self.item = item
        self.itemAccess = itemAccess
        
    @property
    def name(self):
        return self.item.name
        
    @property
    def subNodes(self):
        """Returns always [] because we don't have sub nodes.
        """

        return []
    
    def getSubNode(self, pathElement):
        """Returns always None as item nodes don't have sub nodes.
        """
        return None
    
    @property
    @cache
    def attr(self):
        st = MyStat()
        st.st_mode = stat.S_IFLNK | 0444
        st.st_nlink = 2
            
        return st
    
    @property
    @cache
    def direntry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFLNK
        
        return e
    
    @property
    @cache
    def link(self):
        return self.itemAccess.getItemDirectory(self.name)
    
    def __repr__(self):
        return '<ItemNode %s>' % self.name
    
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
    
    @property
    @cache
    def attr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
            
        return st
    
    @property
    @cache
    def direntry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e
    
class TagValueNode(ContainerNode):
    
    def __init__(self, parentNode, tagValue, itemAccess):
        super(TagValueNode, self).__init__(parentNode)
        self.tagValue = tagValue
        self.itemAccess = itemAccess
        
    @property
    def name(self):
        return self.tagValue
        
    @property
    @cache
    def _myFilter(self):
        return TagValueFilter(self.tagValue)
    
    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'tags',
                                   [TagValueNode(self, tag.value, self.itemAccess) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for tag value %s: %s', self.tagValue, subNodes)
        
        return subNodes
    
class TagNode(ContainerNode):
    
    def __init__(self, parentNode, tag, itemAccess):
        super(TagNode, self).__init__(parentNode)
        self.tag = tag
        self.itemAccess = itemAccess
        
    @property
    def name(self):
        return self.tag.value
        
    @property
    @cache
    def _myFilter(self):
        return TagFilter(self.tag)
    
    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'tags',
                                   [TagValueNode(self, tag.value, self.itemAccess) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for %s: %s', self.tag, subNodes)
        
        return subNodes
    
class ContextTagNode(ContainerNode):
    
    def __init__(self, parentNode, tag, itemAccess):
        super(ContextTagNode, self).__init__(parentNode)
        self.tag = tag
        self.itemAccess = itemAccess
        
    @property
    def name(self):
        return self.tag.value
        
    @property
    @cache
    def _myFilter(self):
        return TagFilter(self.tag)

    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'tags',
                                   [TagNode(self, tag, self.itemAccess) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for %s: %s', self, subNodes)
        
        return subNodes

class ContextContainerNode(ContainerNode):
    
    def __init__(self, parentNode, context, itemAccess):
        super(ContextContainerNode, self).__init__(parentNode)
        self.context = context
        self.itemAccess = itemAccess
        
    @property
    def name(self):
        return self.context
        
    @property
    def filter(self):
        return self.parentNode.filter
    
    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'tags',
                          [tagNode for tagNode in [ContextTagNode(self, tag, self.itemAccess) for tag in self.itemAccess.contextTags(self.context)]])
        
        logging.debug('Sub nodes for %s: %s', self, subNodes)
        
        return subNodes

class RootNode(Node):
    
    def __init__(self, itemAccess):
        self.itemAccess = itemAccess
        self.filterTags = []
        
    @property
    @cache
    def filter(self):
        return NoneFilter()
        
    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'untagged items',
                          [UntaggedItemsNode('.untagged', self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in self.itemAccess.items.itervalues()])
        self._addSubNodes(subNodes,
                          'contexts',
                          [ContextContainerNode(self, context, self.itemAccess) for context in self.itemAccess.contexts])
        self._addSubNodes(subNodes,
                          'tags',
                          [TagValueNode(self, tag.value, self.itemAccess) for tag in self.itemAccess.tags])
        
        return subNodes
        
    @property
    @cache
    def attr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2

        return st
    
    @property
    def direntry(self):
        return None
    
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
