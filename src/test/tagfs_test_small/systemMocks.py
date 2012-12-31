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

class ReadLineFileMock(object):

    def __init__(self, lines):
        self.lines = lines

    def __enter__(self, *args, **kwargs):
        return self.lines

    def __exit__(self, *args, **kwargs):
        pass

class SystemMock(object):

    def __init__(self, test, readFiles = {}):
        self.test = test
        self.readFiles = readFiles

    def open(self, fileName, mode):
        if(mode == 'r'):
            return self.readFiles[fileName]

        self.test.fail('Unknown file mode %s' % mode)
