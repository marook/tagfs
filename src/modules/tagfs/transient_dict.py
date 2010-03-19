#
# Copyright 2010 Markus Pielmeier
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

class TransientDict(object):

    class Version(object):
        
        def __init__(self, key):
            self.key = key

        def touch(self, version):
            self.version = version

    class Value(object):
        
        def __init__(self, value, version):
            self.value = value
            self.version = version

    def __init__(self, averageCapacity):
        self.averageCapacity = averageCapacity
        self.nextVersion = 0
        self.setCounter = 0
        self.data = {}
        self.versions = []
    
    def __getitem__(self, k):
        v = self.data[k]

        if not v:
            return None

        v.version.touch(self.nextVersion)
        self.nextVersion += 1

        return v.value

    def _cleanUpCache(self):
        if len(self.data) < self.averageCapacity:
            return

        def versionCmp(a, b):
            if a.version < b.version:
                return 1
            if b.version < a.version:
                return -1

            return 0

        self.versions.sort(versionCmp)

        while len(self.versions) > self.averageCapacity:
            version = self.versions.pop()

            self.data.pop(version.key)

    def __setitem__(self, k, v):
        if k in self.data:
            value = self.data[k]

            value.value = v
        else:
            self.setCounter += 1
            if self.setCounter % self.averageCapacity == 0:
                self._cleanUpCache()

            version = TransientDict.Version(k)
            self.versions.append(version)

            value = TransientDict.Value(v, version)
            self.data[k] = value

        value.version.touch(self.nextVersion)
        self.nextVersion += 1

    def __contains__(self, k):
        return k in self.data
