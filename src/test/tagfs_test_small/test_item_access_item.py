#
# Copyright 2012 Markus Pielmeier
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

import unittest

import tagfs.item_access as item_access
import systemMocks

class ItemAccessMock(object):

    def __init__(self, dataDirectory, tagFileName):
        self.dataDirectory = dataDirectory
        self.tagFileName = tagFileName

class FreebaseQueryParserMock(object):

    def __init__(self, test):
        self.test = test

    def parse(self, queryString):
        return queryString

class FreebaseAdapterMock(object):

    def __init__(self, test):
        self.test = test

    def execute(self, query):
        return {
            'freebaseContext': ['freebaseValue'],
            }

class WhenItemHasFreebaseQueryTag(unittest.TestCase):

    def setUp(self):
        super(WhenItemHasFreebaseQueryTag, self).setUp()

        self.system = systemMocks.SystemMock(self)
        self.system.readFiles['/path/to/my/data/directory/myItem/.tag'] = systemMocks.ReadLineFileMock(['_freebase: myFreebaseQuery',])

        self.itemAccess = ItemAccessMock('/path/to/my/data/directory', '.tag')
        self.freebaseQueryParser = FreebaseQueryParserMock(self)
        self.freebaseAdapter = FreebaseAdapterMock(self)

        self.item = item_access.Item('myItem', self.system, self.itemAccess, self.freebaseQueryParser, self.freebaseAdapter)

    def testThenItemHasFreebaseTaggingsFromItemAccess(self):
        self.assertEqual(list(self.item.getTagsByContext('freebaseContext')), [item_access.Tag('freebaseValue', 'freebaseContext'),])
