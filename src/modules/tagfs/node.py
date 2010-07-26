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

import fuse
import logging
import stat
import time

from cache import cache
import item_access

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

    def __str__(self):
        return '[' + ', '.join([field + ': ' + str(self.__dict__[field]) for field in self.__dict__]) + ']'

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
    
class DirectoryNode(Node):

    def getattr(self, path):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
        st.st_mtime = self.itemAccess.parseTime
        st.st_ctime = st.st_mtime
        st.st_atime = st.st_mtime
            
        return st
    
    @property
    @cache
    def direntry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFDIR
        
        return e

    def readdir(self, path, offset):
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')

        for n in self.subNodes:
            yield fuse.Direntry(n.name)


class ContainerNode(DirectoryNode):
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
        
    @cache
    # DANGER! we can only cache this method because we know that the items from
    # our parent will never ever change! 
    def required(self, items):
        selfItems = self.items
        selfItemsLen = len(self.items)
        
        return not selfItemsLen == 0 and not selfItemsLen == len(items)
            
    @property
    @cache
    def filter(self):
        parentFilter = self.parentNode.filter
        
        return item_access.AndFilter([parentFilter, self._myFilter])
    
    @property
    @cache
    def items(self):
        items = self.itemAccess.filterItems(self.filter)
        
        logging.debug('Items request for %s: %s',
                      self,
                      [item.name for item in items])
        
        return items

class ItemNode(Node):
    
    def __init__(self, item, itemAccess, prefix = None):
        self.item = item
        self.itemAccess = itemAccess
        self.prefix = prefix
        
    @property
    def name(self):
        if not self.prefix:
            return self.item.name

        return self.prefix + self.item.name
        
    @property
    def subNodes(self):
        """Returns always [] because we don't have sub nodes.
        """

        return []
    
    def getSubNode(self, pathElement):
        """Returns always None as item nodes don't have sub nodes.
        """
        return None
    
    def getattr(self, path):
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
    
    def readlink(self, path):
        return self.item.itemDirectory
    
    def __repr__(self):
        return '<ItemNode %s>' % self.name
    
class CsvExportNode(Node):

    COL_SEPARATOR = ';'

    TEXT_CHAR = '"'

    ROW_SEPARATOR = '\n'

    def __init__(self, parentNode, itemAccess):
        self.name = 'export.csv'
        self.parentNode = parentNode
        self.itemAccess = itemAccess

    def formatRow(self, row):
        first = True

        s = ''

        for col in row:
            if first:
                first = False
            else:
                s = s + CsvExportNode.COL_SEPARATOR

            # TODO escape TEXT_CHAR in col string
            s = s + CsvExportNode.TEXT_CHAR + str(col) + CsvExportNode.TEXT_CHAR

        s = s + CsvExportNode.ROW_SEPARATOR

        return s

    @property
    def filter(self):
        return self.parentNode.filter
    
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
    def content(self):
        contexts = set()
        for i in self.items:
            for t in i.tags:
                contexts.add(t.context)

        s = ''

        headline = ['name', ]
        for c in contexts:
            headline.append(c)
        s = s + self.formatRow(headline)

        for i in self.items:
            row = [i.name, ]

            for c in contexts:
                row.append('\n'.join(i.getTagsByContext(c)))

            s = s + self.formatRow(row)

        return s

    @property
    def subNodes(self):
        """Returns always [] because we don't have sub nodes.
        """

        return []
    
    def getSubNode(self, pathElement):
        """Returns always None as file nodes don't have sub nodes.
        """
        return None
    
    def getattr(self, path):
        a = MyStat()
        a.st_mode = stat.S_IFREG | 0444
        a.st_nlink = 2
        # TODO bug: len of content is not size of content in bytes (unicode!)
        a.st_size = len(self.content)

        return a

    @property
    @cache
    def direntry(self):
        e = fuse.Direntry(self.name)
        e.type = stat.S_IFREG
        
        return e
    
    def open(self, path, flags):
        pass

    def read(self, path, size, offset):
        return self.content[offset:size - offset]

class ExportDirectoryNode(DirectoryNode):

    def __init__(self, name, parentNode, itemAccess):
        self.name = name
        self.parentNode = parentNode
        self.itemAccess = itemAccess

    @cache
    def _getSubNodesDict(self):
        subNodes = {}

        self._addSubNodes(subNodes,
                          'csv',
                          [CsvExportNode(self, self.itemAccess), ])
        
        return subNodes

    @property
    def filter(self):
        return self.parentNode.filter

class UntaggedItemsNode(DirectoryNode):
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
    
class ReviewItemsNode(DirectoryNode):

    def __init__(self, name, itemAccess):
        self.name = name
        self.itemAccess = itemAccess

    @cache
    def _getSubNodesDict(self):
        items = [i for i in self.itemAccess.items.itervalues() if i.tagged]
        items.sort(key = lambda i: i.tagsModificationTime)
        prefixWidth = len(str(len(items)))

        def prefix(i):
            return str(i).rjust(prefixWidth, '0')

        subNodes = {}

        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess, prefix = prefix(i) + ' ') for i, item in enumerate(items)])

        return subNodes

class TagValueNode(ContainerNode):
    
    def __init__(self, parentNode, tagValue, itemAccess, config):
        super(TagValueNode, self).__init__(parentNode)
        self.tagValue = tagValue
        self.itemAccess = itemAccess
        self.config = config
        
    @property
    def name(self):
        return self.tagValue
        
    @property
    @cache
    def _myFilter(self):
        return item_access.TagValueFilter(self.tagValue)
    
    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'contexts',
                                   [ContextContainerNode(self, context, self.itemAccess, self.config) for context in self.itemAccess.contexts])

        if self.config.enableValueFilters:
            self._addSubContainerNodes(subNodes,
                                       'tags',
                                       [TagValueNode(self, tag.value, self.itemAccess, self.config) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for tag value %s: %s', self.tagValue, subNodes)
        
        return subNodes
    
class TagNode(ContainerNode):
    
    def __init__(self, parentNode, tag, itemAccess, config):
        super(TagNode, self).__init__(parentNode)
        self.tag = tag
        self.itemAccess = itemAccess
        self.config = config
        
    @property
    def name(self):
        return self.tag.value
        
    @property
    @cache
    def _myFilter(self):
        return item_access.TagFilter(self.tag)
    
    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'tags',
                                   [TagValueNode(self, tag.value, self.itemAccess, self.config) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for %s: %s', self.tag, subNodes)
        
        return subNodes
    
class ContextTagNode(ContainerNode):
    
    def __init__(self, parentNode, tag, itemAccess, config):
        super(ContextTagNode, self).__init__(parentNode)
        self.tag = tag
        self.itemAccess = itemAccess
        self.config = config
        
    @property
    def name(self):
        return self.tag.value
        
    @property
    @cache
    def _myFilter(self):
        return item_access.TagFilter(self.tag)

    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        self._addSubContainerNodes(subNodes,
                                   'contexts',
                                   [ContextContainerNode(self, context, self.itemAccess, self.config) for context in self.itemAccess.contexts])

        if self.config.enableValueFilters:
            self._addSubContainerNodes(subNodes,
                                       'tags',
                                       [TagNode(self, tag, self.itemAccess, self.config) for tag in self.itemAccess.tags])
        
        logging.debug('Sub nodes for %s: %s', self, subNodes)
        
        return subNodes

class ContextNotSetNode(ContainerNode):

    def __init__(self, parentNode, context, itemAccess):
        super(ContextNotSetNode, self).__init__(parentNode)
        self.context = context
        self.itemAccess = itemAccess

    @property
    def name(self):
        return '.unset'
        
    @property
    @cache
    def _myFilter(self):
        return item_access.NotContextFilter(self.context)

    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'items',
                          [ItemNode(item, self.itemAccess) for item in items])
        
        logging.debug('Sub nodes for %s: %s', self, subNodes)
        
        return subNodes

class ContextContainerNode(ContainerNode):
    """Contains directories for the target context's values.
    
    @attention: This node can only be contained by nodes which got an items
    property. Reason is parentNode.items call in contextTagNodes(self) method.
    """
    
    def __init__(self, parentNode, context, itemAccess, config):
        super(ContextContainerNode, self).__init__(parentNode)
        self.context = context
        self.itemAccess = itemAccess
        self.config = config
        
    def required(self, items):
        for tagNode in self.contextTagNodes:
            if tagNode.required(items):
                return True
            
        return False

    @property
    def name(self):
        return self.context
        
    @property
    def filter(self):
        return self.parentNode.filter
    
    @property
    @cache
    def contextTagNodes(self):
        return [ContextTagNode(self, tag, self.itemAccess, self.config) for tag in self.itemAccess.contextTags(self.context)]

    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'not_context',
                          [ContextNotSetNode(self, self.context, self.itemAccess),])
        self._addSubNodes(subNodes,
                          'tags',
                          self.contextTagNodes)
        
        logging.debug('Sub nodes for %s: %s', self, subNodes)
        
        return subNodes

class TagValueContainerNode(ContainerNode):
    
    def __init__(self, parentNode, itemAccess, config):
        super(TagValueContainerNode, self).__init__(parentNode)
        self.itemAccess = itemAccess
        self.config = config

    @property
    def name(self):
        return '.any_context'

    @property
    def filter(self):
        return self.parentNode.filter
    
    @cache
    def _getSubNodesDict(self):
        items = self.items
        
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])
        self._addSubContainerNodes(subNodes,
                                   'tags',
                                   [TagValueNode(self, tag.value, self.itemAccess, self.config) for tag in self.itemAccess.tags])
        
        return subNodes

class RootNode(DirectoryNode):
    
    def __init__(self, itemAccess, config):
        self.itemAccess = itemAccess
        self.config = config
        self.filterTags = []
        
    @property
    @cache
    def filter(self):
        return item_access.NoneFilter()
        
    @cache
    def _getSubNodesDict(self):
        subNodes = {}
        
        self._addSubNodes(subNodes,
                          'untagged items',
                          [UntaggedItemsNode('.untagged', self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'review items',
                          [ReviewItemsNode('.review', self.itemAccess), ])
        self._addSubNodes(subNodes,
                          'export',
                          [ExportDirectoryNode('.export', self, self.itemAccess), ])

        if self.config.enableRootItemLinks:
            self._addSubNodes(subNodes,
                              'items',
                              [ItemNode(item, self.itemAccess) for item in self.itemAccess.items.itervalues()])

        self._addSubNodes(subNodes,
                          'contexts',
                          [ContextContainerNode(self, context, self.itemAccess, self.config) for context in self.itemAccess.contexts])

        if self.config.enableValueFilters:
            self._addSubNodes(subNodes,
                              'tags',
                              [TagValueNode(self, tag.value, self.itemAccess, self.config) for tag in self.itemAccess.tags])
        else:
            self._addSubNodes(subNodes,
                              'tags container',
                              [TagValueContainerNode(self, self.itemAccess, self.config), ])
        
        return subNodes
        
    @property
    @cache
    def attr(self):
        st = MyStat()
        st.st_mode = stat.S_IFDIR | 0555
        st.st_nlink = 2
        st.st_mtime = time.time()
        st.st_ctime = st.st_mtime
        st.st_atime = st.st_mtime

        return st
    
    @property
    def direntry(self):
        return None
