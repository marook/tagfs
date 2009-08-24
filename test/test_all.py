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

class TestTestCaseEnvironment(unittest.TestCase):
    """Makes sure the environment for the test case is set up right.
    """
    
    def testCwd(self):
        """Makes sure that the current working directory is correct.
        """
        
        import os
        
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'etc/test/events')))

class TestItem(unittest.TestCase):
    """This is a test case for the Item class.
    """
    
    class MyItemAccess(object):
        """This is a mock object for the ItemAccess class.
        """
        
        def __init__(self):
            self.dataDirectory = 'etc/test/events'
            self.tagFileName = '.tag'
    
    def setUp(self):
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
        
        self.assertEqual(set(['holiday', 'airport', 'india']), item.tags)
        self.assertAlmostEqual(1250195650.7, item.tagsModificationTime, 1)
        self.assertAlmostEqual(1250195650.7, item.tagsCreationTime, 1)
        self.assertTrue(item.tagged)

class TestItemAccess(unittest.TestCase):
    """Test the tagfs.ItemAccess class.
    """

    def setUp(self):
        self.itemAccess = tagfs.ItemAccess('etc/test/events', '.tag')

    def testItems(self):
        """Test the items property of ItemAccess.
        """
        items = self.itemAccess.items
        
        self.assertEqual(set(['2008-03-29 - holiday south korea', '2008-12-25 - holiday india']), set(items))

    def testTags(self):
        """Test the tag property of ItemAccess
        """
        
        tags = self.itemAccess.tags
        
        self.assertEqual(set(['airport', 'holiday', 'india', 'korea']), set(tags))
        
    def testUntagged(self):
        """Test the untaggedItems property of ItemAccess
        """
        
        untaggedItems = self.itemAccess.untaggedItems
        
        self.assertEqual(set(['2009-07-29 - no tags']), set(untaggedItems))
        
    def __testFilter(self, filters, expectedResultItems, expectedResultTags):
        resultItems, resultTags = self.itemAccess.filter(filters)
        
        self.assertEqual(set(expectedResultItems), set(resultItems))
        self.assertEqual(set(expectedResultTags), set(resultTags))
    
    def testFilterSingle(self):
        """Tests a single filter argument.
        """
        
        self.__testFilter(['korea'],
                          ['2008-03-29 - holiday south korea'],
                          ['airport', 'holiday'])

    def testFilterMultiple(self):
        """Tests multiple filter arguments at once.
        """
        
        self.__testFilter(['korea', 'airport'],
                          ['2008-03-29 - holiday south korea'],
                          ['holiday'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    import sys, os.path

    testdir = os.path.dirname(os.path.abspath(__file__))
    srcdir = os.path.join(os.path.split(testdir)[0], 'src')
    eventsdir = os.path.join(os.path.split(testdir)[0], 'etc', 'test', 'events')

    for x in (testdir, srcdir, eventsdir):
        assert os.path.exists(x), "Directory not found: %s" % x

    sys.path.extend((testdir, srcdir))

    import tagfs

    unittest.main()
