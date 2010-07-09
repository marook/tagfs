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
import tagfs.item_access as item_access
import tagfs.node as node

def createTestItemAccess():
    return item_access.ItemAccess(eventsdir, '.tag')

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
        
        tags = item_access.parseTagsFromFile(tagFileName)
        
        expectedTags = set([item_access.Tag('holiday'),
                            item_access.Tag('airport'),
                            item_access.Tag('korea'),
                            item_access.Tag('tube', context = 'object'),
                            item_access.Tag('Markus Pielmeier', context = 'creator')])
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
        
        item = item_access.Item('no such item', self.itemAccess)
        
        self.assertFalse(os.path.isdir(item.itemDirectory))
        
        self.assertEqual(None, item.tags)
        self.assertEqual(None, item.tagsModificationTime)
        self.assertEqual(None, item.tagsCreationTime)
        self.assertFalse(item.tagged)
        
    def testItemNoTagsItem(self):
        """Tests the results for items which got no tags assigned.
        """
        
        item = item_access.Item('2009-07-29 - no tags', self.itemAccess)
        
        self.assertTrue(os.path.isdir(item.itemDirectory))
        
        self.assertEqual(None, item.tags)
        self.assertEqual(None, item.tagsModificationTime)
        self.assertEqual(None, item.tagsCreationTime)
        self.assertFalse(item.tagged)
        
    def testItem(self):
        """Tests an item with tags assigned to.
        """
        
        item = item_access.Item('2008-12-25 - holiday india', self.itemAccess)
        
        self.assertTrue(os.path.isdir(item.itemDirectory))
        
        expectedTags = set([item_access.Tag('holiday'),
                            item_access.Tag('airport'),
                            item_access.Tag('india'),
                            item_access.Tag('Markus Pielmeier', context = 'creator')])
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
        
        expectedTags = set([item_access.Tag('airport'),
                            item_access.Tag('holiday'),
                            item_access.Tag('india'),
                            item_access.Tag('korea'),
                            item_access.Tag('Markus Pielmeier', context = 'creator'),
                            item_access.Tag('Tama Yuri', context = 'creator'),
                            item_access.Tag('flickr', context = 'source'),
                            item_access.Tag('tube', context = 'object')])
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
        
        self._testFilter(item_access.TagValueFilter('korea'),
                         ['2008-03-29 - holiday south korea'])

    def testFilterMultiple(self):
        """Tests AndFilter filter arguments at once.
        
        @see: tagfs.AndFilter
        """
        
        self._testFilter(item_access.AndFilter([item_access.TagValueFilter('korea'),
                                                item_access.TagValueFilter('airport')]),
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
        
        # TODO supply correct path to node.getattr
        attr = node.getattr('/path')
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
        
        item = item_access.Item('test', self.itemAccess)
        
        n = node.ItemNode(item, self.itemAccess)
        
        self._testNodeInterface(n)
    
        direntry = n.direntry
        self.assertEqual('test', direntry.name)
        self.assertEqual(stat.S_IFLNK, direntry.type)
        
        # TODO supply correct path to n.readlink
        self.assertNotEqual(None, n.readlink('/path'))
        
class TestUntaggedItemsNode(AbstractNodeTest):
    """This test case tests the UntaggedItemsNode.
    """
    
    def testUntaggedItemsNodeInterface(self):
        n = node.UntaggedItemsNode('.untagged', self.itemAccess)
        
        self._testNodeInterface(n)

        direntry = n.direntry
        self.assertEqual('.untagged', direntry.name)
        
class TestTagNode(AbstractNodeTest):
    """This test case tests the TagNode class.
    """
    
    def testTagNode(self):
        c = tagfs.Config()

        parentNode = node.RootNode(self.itemAccess, c)
        
        n = node.TagNode(parentNode, item_access.Tag('holiday'), self.itemAccess, c)
        
        self._testNodeInterface(n)

class TestRootNode(AbstractNodeTest):
    """This test case tests the RootNode class.
    """
    
    def testRootNode(self):
        c = tagfs.Config()

        n = node.RootNode(self.itemAccess, c)
        
        self._testNodeInterface(n)
        
class TestNodeRecurse(AbstractNodeTest):
    """This test recurses through a RootNode and it's children.
    
    This test case tries to call many of the node functions to get a overall
    performance measure.
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        
        self.itemAccess = createTestItemAccess()
        
    def __recurseNode(self, n):
        self._testNodeInterface(n)
        
        nDir = set(dir(n))
        
        if 'required' in nDir:
            n.required([])
            
        if 'filter' in nDir:
            self.assertNotEqual(None, n.filter)
        
        for sn in n.subNodes:
            self.__recurseNode(sn)
    
    def testRecurse(self):
        c = tagfs.Config()

        n = node.RootNode(self.itemAccess, c)
        
        self.__recurseNode(n)
        

if __name__ == "__main__":
    setupenv()
    import tagfs

    if 'PROFILE' in os.environ:
        import cProfile
        
        profileFile = os.path.join(os.getcwd(), 'tagfs_test.profile')
        
        cProfile.run('unittest.main()', profileFile)
    else:
        unittest.main()
