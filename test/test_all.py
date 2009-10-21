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

import logging
import unittest
import os
import sys

def setupenv():
    from os.path import dirname, abspath, exists, join as pjoin, split as psplit

    global eventsdir
    testdir = dirname(abspath(__file__))
    projectdir = pjoin(psplit(testdir)[0])
    srcdir = pjoin(projectdir, 'src')
    moddir = pjoin(srcdir, 'modules')
    eventsdir = pjoin(projectdir, 'etc', 'test', 'events')

    for x in (testdir, srcdir, moddir, eventsdir):
        assert exists(x), "Directory not found: %s" % x

    sys.path.insert(0, testdir)
    sys.path.insert(0, moddir)
    sys.path.insert(0, srcdir)

setupenv()
import tagfs

def createTestItemAccess():
    return tagfs.ItemAccess(eventsdir, '.tag')

class TestTestCaseEnvironment(unittest.TestCase):
    """Makes sure the environment for the test case is set up right.
    """
    
    def testCwd(self):
        """Makes sure that the events directory is accessible.
        """
        
        import os
        
        self.assertTrue(os.path.exists(eventsdir))

class TestParseTagsFromFile(unittest.TestCase):
    
    def testParse(self):
        """Tests the parseTagsFromFile(...) method.
        """
        
        tagFileName = os.path.join(eventsdir,
                                   '2008-03-29 - holiday south korea',
                                   '.tag')
        
        tags = tagfs.parseTagsFromFile(tagFileName)
        
        expectedTags = set([tagfs.Tag('holiday'),
                            tagfs.Tag('airport'),
                            tagfs.Tag('korea'),
                            tagfs.Tag('Markus Pielmeier', context = 'creator')])
        self.assertEqual(expectedTags, tags)
        

class TestItem(unittest.TestCase):
    """This is a test case for the Item class.
    """
    
    class MyItemAccess(object):
        """This is a mock object for the ItemAccess class.
        """
        
        def __init__(self):
            self.dataDirectory = eventsdir
            self.tagFileName = '.tag'
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.itemAccess = TestItem.MyItemAccess()
    
    def testItemNotExists(self):
        """Tests the results for items which don't exist.
        """
        
        item = tagfs.Item('no such item', self.itemAccess)
        
        self.assertFalse(os.path.isdir(item.itemDirectory))
        
        self.assertEqual(None, item.tags)
        self.assertEqual(None, item.tagsModificationTime)
        self.assertEqual(None, item.tagsCreationTime)
        self.assertFalse(item.tagged)
        
    def testItemNoTagsItem(self):
        """Tests the results for items which got no tags assigned.
        """
        
        item = tagfs.Item('2009-07-29 - no tags', self.itemAccess)
        
        self.assertTrue(os.path.isdir(item.itemDirectory))
        
        self.assertEqual(None, item.tags)
        self.assertEqual(None, item.tagsModificationTime)
        self.assertEqual(None, item.tagsCreationTime)
        self.assertFalse(item.tagged)
        
    def testItem(self):
        """Tests an item with tags assigned to.
        """
        
        item = tagfs.Item('2008-12-25 - holiday india', self.itemAccess)
        
        self.assertTrue(os.path.isdir(item.itemDirectory))
        
        expectedTags = set([tagfs.Tag('holiday'),
                            tagfs.Tag('airport'),
                            tagfs.Tag('india'),
                            tagfs.Tag('Markus Pielmeier', context = 'creator')])
        self.assertEqual(expectedTags, item.tags)
        # TODO disabled timestamp tests until time in test is not human readable
        #self.assertAlmostEqual(1250195650.7, item.tagsModificationTime, 1)
        #self.assertAlmostEqual(1250195650.7, item.tagsCreationTime, 1)
        self.assertTrue(item.tagged)

class TestItemAccess(unittest.TestCase):
    """Test the tagfs.ItemAccess class.
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.itemAccess = createTestItemAccess()

    def testItems(self):
        """Test the items property of ItemAccess.
        """
        items = self.itemAccess.items
        
        expectedItems = set(['2008-03-29 - holiday south korea',
                             '2008-12-25 - holiday india',
                             '2009-07-29 - no tags',
                             '2008-11-11 - airport underground railway'])
        self.assertEqual(expectedItems,
                         set(items))

    def testTags(self):
        """Test the tag property of ItemAccess
        """
        
        tags = self.itemAccess.tags
        
        expectedTags = set([tagfs.Tag('airport'),
                            tagfs.Tag('holiday'),
                            tagfs.Tag('india'),
                            tagfs.Tag('korea'),
                            tagfs.Tag('Markus Pielmeier', context = 'creator'),
                            tagfs.Tag('Tama Yuri', context = 'creator'),
                            tagfs.Tag('flickr', context = 'source')])
        self.assertEqual(expectedTags,
                         set(tags))
        
    def testTaggedItems(self):
        """Test the items property of ItemAccess.
        """
        items = self.itemAccess.taggedItems
        
        expectedItems = set(['2008-03-29 - holiday south korea',
                             '2008-12-25 - holiday india',
                             '2008-11-11 - airport underground railway'])
        self.assertEqual(expectedItems,
                         set([item.name for item in items]))

    def testUntaggedItems(self):
        """Test the untaggedItems property of ItemAccess
        """
        
        untaggedItems = self.itemAccess.untaggedItems
        
        self.assertEqual(set(['2009-07-29 - no tags']),
                         set([item.name for item in untaggedItems]))
        
    def _testFilter(self, filters, expectedResultItems):
        resultItems = self.itemAccess.filterItems(filters)
        
        self.assertEqual(set(expectedResultItems),
                         set([item.name for item in resultItems]))
    
    def testFilterSingle(self):
        """Tests TagValueFilter filter argument.
        
        @see: tagfs.TagValueFilter
        """
        
        self._testFilter(tagfs.TagValueFilter('korea'),
                         ['2008-03-29 - holiday south korea'])

    def testFilterMultiple(self):
        """Tests AndFilter filter arguments at once.
        
        @see: tagfs.AndFilter
        """
        
        self._testFilter(tagfs.AndFilter([tagfs.TagValueFilter('korea'),
                                          tagfs.TagValueFilter('airport')]),
                         ['2008-03-29 - holiday south korea'])

class AbstractNodeTest(unittest.TestCase):
    """This abstract TestCase checks the Node interface definitions.
    """
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.itemAccess = createTestItemAccess()
    
    def _testNodeInterface(self, node):
        """This method tests wether the node implements the node interface contract.
        """
        
        self.assertNotEqual(None, node)
        
        for subNode in node.subNodes:
            self._testNodeInterface(subNode)

        self.assertTrue('getSubNode' in set(dir(node)))
        
        attr = node.attr
        self.assertNotEqual(None, attr.st_mode)

        direntry = node.direntry
        if direntry is not None:
            self.assertNotEqual(None, direntry.name)
            self.assertNotEqual(None, direntry.type)

class TestItemNode(AbstractNodeTest):
    """This test case tests the ItemNode class.
    """
    
    def testItemNodeInterface(self):
        import stat
        
        item = tagfs.Item('test', self.itemAccess)
        
        node = tagfs.ItemNode(item, self.itemAccess)
        
        self._testNodeInterface(node)
    
        direntry = node.direntry
        self.assertEqual('test', direntry.name)
        self.assertEqual(stat.S_IFLNK, direntry.type)
        
        self.assertNotEqual(None, node.link)
        
class TestUntaggedItemsNode(AbstractNodeTest):
    """This test case tests the UntaggedItemsNode.
    """
    
    def testUntaggedItemsNodeInterface(self):
        node = tagfs.UntaggedItemsNode('.untagged', self.itemAccess)
        
        self._testNodeInterface(node)

        direntry = node.direntry
        self.assertEqual('.untagged', direntry.name)
        
class TestTagNode(AbstractNodeTest):
    """This test case tests the TagNode class.
    """
    
    def testTagNode(self):
        parentNode = tagfs.RootNode(self.itemAccess)
        
        node = tagfs.TagNode(parentNode, tagfs.Tag('holiday'), self.itemAccess)
        
        self._testNodeInterface(node)

class TestRootNode(AbstractNodeTest):
    """This test case tests the RootNode class.
    """
    
    def testRootNode(self):
        node = tagfs.RootNode(self.itemAccess)
        
        self._testNodeInterface(node)

if __name__ == "__main__":
    setupenv()
    import tagfs
    unittest.main()
