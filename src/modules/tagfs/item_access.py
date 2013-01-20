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
import traceback

from cache import cache
import sysIO
import freebase_support

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

def parseTagsFromFile(system, tagFileName):
    """Parses the tags from the specified file.
    
    @return: The parsed values are returned as a set containing Tag objects.
    @see: Tag
    """
    
    tags = set()
    
    with system.open(tagFileName, 'r') as tagFile:
        for rawTag in tagFile:
            rawTag = rawTag.strip()
            
            try:
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
            except:
                logging.warning('Skipping tagging \'%s\' from file \'%s\' as it can\'t be parsed\n%s.' % (rawTag, tagFileName, traceback.format_exc()))
        
    return tags
    
class NoSuchTagValue(Exception):

    pass

class Item(object):
    
    def __init__(self, name, system, itemAccess, freebaseQueryParser, freebaseAdapter, genericFreebaseQueries = [], parseTagsFromFile = parseTagsFromFile):
        self.name = name
        self.system = system
        self.itemAccess = itemAccess
        self.freebaseQueryParser = freebaseQueryParser
        self.freebaseAdapter = freebaseAdapter
        self.parseTagsFromFile = parseTagsFromFile
        self.genericFreebaseQueries = genericFreebaseQueries
        
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
        
        return os.path.join(self.itemDirectory, self.itemAccess.tagFileName)

    @property
    @cache
    def tagFileExists(self):
        return self.system.pathExists(self._tagFileName)

    def __getFreebaseTags(self, query):
        try:
            for context, values in self.freebaseAdapter.execute(query).iteritems():
                for value in values:
                    # without the decode/encode operations fuse refuses to show
                    # directory entries which are based on freebase data
                    yield Tag(value.decode('ascii', 'ignore').encode('ascii'), context)
        except Exception as e:
            logging.error('Failed to execute freebase query %s: %s', query, e)
    
    def __parseTags(self):
        tagFileName = self._tagFileName
        
        for rawTag in self.parseTagsFromFile(self.system, tagFileName):
            if(rawTag.context == '_freebase'):
                query = self.freebaseQueryParser.parse(rawTag.value)
                
                for tag in self.__getFreebaseTags(query):
                    yield tag
            else:
                yield rawTag

    @property
    @cache
    def tagsCreationTime(self):
        if not self.tagFileExists:
            return None

        return os.path.getctime(self._tagFileName)
    
    @property
    @cache
    def tagsModificationTime(self):
        """Returns the last time when the tags have been modified.
        """
        
        if not self.tagFileExists:
            return None

        return os.path.getmtime(self._tagFileName)
    
    @property
    @cache
    def tags(self):
        """Returns the tags as a list for this item.
        """
        
        if not self.tagFileExists:
            return None

        tags = list(self.__parseTags())

        def getValue(context):
            for tag in tags:
                if(tag.context == context):
                    return tag.value

            raise NoSuchTagValue()

        queryFactory = freebase_support.GenericQueryFactory(getValue)
        for genericQuery in self.genericFreebaseQueries:
            try:
                query = queryFactory.createQuery(genericQuery.queryObject)

                for tag in self.__getFreebaseTags(freebase_support.Query(query)):
                    tags.append(tag)
            except NoSuchTagValue:
                pass

        return tags

    @property
    def values(self):
        for t in self.tags:
            yield t.value

    def getTagsByContext(self, context):
        for t in self.tags:
            if context != t.context:
                continue

            yield t

    def getValuesByContext(self, context):
        return [t.value for t in self.getTagsByContext(context)]

    def getValueByContext(self, context):
        values = self.getValuesByContext(context)
        valuesLen = len(values)
        
        if(valuesLen == 0):
            return None

        if(valuesLen == 1):
            return values[0]

        raise Exception('Too many values found for context %s' % (context,))

    def isTaggedWithContextValue(self, context, value):
        for t in self.getTagsByContext(context):
            if value == t.value:
                return True

        return False

    def isTaggedWithContext(self, context):
        # TODO don't create whole list... just check wheather list is empty
        return (len([c for c in self.getTagsByContext(context)]) > 0)

    def isTaggedWithValue(self, value):
        for v in self.values:
            if value == v:
                return True

        return False
    
    @property
    def tagged(self):
        return self.tagFileExists
    
    def __repr__(self):
        return '<Item %s, %s>' % (self.name, self.tags)
    
class ItemAccess(object):
    """This is the access point to the Items.
    """
    
    def __init__(self, system, dataDirectory, tagFileName, freebaseQueryParser, freebaseAdapter, genericFreebaseQueries):
        self.system = system
        self.dataDirectory = dataDirectory
        self.tagFileName = tagFileName
        self.freebaseQueryParser = freebaseQueryParser
        self.freebaseAdapter = freebaseAdapter
        self.genericFreebaseQueries = genericFreebaseQueries
        
        self.parseTime = 0
        
    def __parseItems(self):
        items = {}
        
        logging.debug('Start parsing items from dir: %s', self.dataDirectory)
        
        for itemName in os.listdir(self.dataDirectory):
            if itemName == '.tagfs':
                # skip directory with configuration
                continue

            try:
                item = Item(itemName, self.system, self, self.freebaseQueryParser, self.freebaseAdapter, self.genericFreebaseQueries)
                
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

    @property
    @cache
    def values(self):
        values = set()

        for tag in self.tags:
            values.add(tag.value)

        return values

    def __str__(self):
        return '[' + ', '.join([field + ': ' + str(self.__dict__[field]) for field in ['dataDirectory', 'tagFileName']]) + ']'
