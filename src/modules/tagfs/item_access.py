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

import logging
import os
import time

from cache import cache

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
        
        return self.__parseTags()
    
    @property
    @cache
    def tagged(self):
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
        self.parseTime = 0
        
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
        
        self.parseTime = time.time()

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
