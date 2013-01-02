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

import json
import logging

def createFreebaseAdapter():
    # freebase is an optional dependency. tagfs should execute even if it's not
    # available.
    try:
        import freebase

        logging.info('freebase support enabled')

        return FreebaseAdapter()
    except ImportError:
        logging.warn('freebase support disabled')

        return FreebaseAdapterStub()
    
class FreebaseAdapterStub(object):

    def execute(self, *args, **kwargs):
        return {}

class FreebaseAdapter(object):

    def execute(self, query):
        import freebase

        fbResult = freebase.mqlread(query.freebaseQuery)

        result = {}

        for key in query.selectedKeys:
            result[key] = fbResult[key]

        return result

class Query(object):

    def __init__(self, queryObject):
        self.queryObject = queryObject

    @property
    def freebaseQuery(self):
        q = {}

        for key, value in self.queryObject.iteritems():
            if(value is None):
                q[key] = []
            else:
                q[key] = value

        return q

    @property
    def queryString(self):
        # TODO this func is only used in tests => remove
        return json.dumps(self.freebaseQuery, separators = (',', ':'))

    @property
    def selectedKeys(self):
        for key, value in self.queryObject.iteritems():
            if(value is None):
                yield key

class QueryParser(object):

    def parse(self, queryString):
        return Query(json.loads(queryString))

class QueryFileParser(object):

    def __init__(self, system, queryParser):
        self.system = system
        self.queryParser = queryParser

    def parseFile(self, path):
        with self.system.open(path, 'r') as f:
            for line in f:
                yield self.queryParser.parse(line)

class GenericQueryFactory(object):

    def __init__(self, resolveVar):
        self.resolveVar = resolveVar

    def evaluate(self, value):
        if(value is None):
            return None

        valueLen = len(value)

        if(valueLen < 2):
            return value

        if(value[0] != '$'):
            return value

        key = value[1:]

        return self.resolveVar(key)

    def createQuery(self, genericQuery):
        q = {}

        for key, genericValue in genericQuery.iteritems():
            value = self.evaluate(genericValue)

            q[key] = value

        return q
