#
# Copyright 2013 Markus Pielmeier
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
import tagfs.freebase_support as freebase_support

class WhenGenericQueryFactoryWithVariables(unittest.TestCase):

    def resolveVar(self, name):
        return self.variables[name]

    def setUp(self):
        super(WhenGenericQueryFactoryWithVariables, self).setUp()

        self.variables = {}
        self.factory = freebase_support.GenericQueryFactory(self.resolveVar)

        self.varValue = 'value'
        self.variables['var'] = self.varValue

    def testResolveExistingVariable(self):
        q = {'key': '$var',}

        self.assertEqual(self.factory.createQuery(q), {'key': self.varValue,})

    def testCreatedQueryIsNewInstance(self):
        q = {}

        self.assertTrue(not q is self.factory.createQuery(q))

    def testGenericQueryIsUntouched(self):
        q = {'key': '$var',}

        self.factory.createQuery(q)

        self.assertEqual(q, {'key': '$var',})

    def testResolveValueToNone(self):
        q = {'key': None,}

        self.assertEqual(self.factory.createQuery(q), q)
