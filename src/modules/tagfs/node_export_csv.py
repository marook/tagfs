#
# Copyright 2011 Markus Pielmeier
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

import stat

from cache import cache
from node import Stat

class ExportCsvFileNode(object):

    COL_SEPARATOR = ';'

    TEXT_CHAR = '"'

    ROW_SEPARATOR = '\n'

    TAG_VALUE_SEPARATOR = '\n'

    def __init__(self, itemAccess, parentNode):
        self.itemAccess = itemAccess
        self.parentNode = parentNode

    @property
    def name(self):
        return 'export.csv'

    @property
    def items(self):
        return self.parentNode.items

    def formatRow(self, row):
        first = True

        for col in row:
            if first:
                first = False
            else:
                yield ExportCsvFileNode.COL_SEPARATOR

            # TODO escape TEXT_CHAR in col string
            yield ExportCsvFileNode.TEXT_CHAR
            yield str(col)
            yield ExportCsvFileNode.TEXT_CHAR

        yield ExportCsvFileNode.ROW_SEPARATOR

    @property
    def _content(self):
        contexts = set()
        for i in self.items:
            for t in i.tags:
                contexts.add(t.context)

        headline = ['name', ]
        for c in contexts:
            headline.append(c)
        for s in self.formatRow(headline):
            yield s

        for i in self.items:
            row = [i.name, ]

            for c in contexts:
                row.append(ExportCsvFileNode.TAG_VALUE_SEPARATOR.join([t.value for t in i.getTagsByContext(c)]))

            for s in self.formatRow(row):
                yield s

    @property
    @cache
    def content(self):
        return ''.join(self._content)

    @property
    def attr(self):
        s = Stat()

        s.st_mode = stat.S_IFREG | 0444
        s.st_nlink = 2

        # TODO replace with memory saving size calculation
        import array
        s.st_size = len(array.array('c', self.content))

        return s

    def open(self, path, flags):
        return

    def read(self, path, size, offset):
        return self.content[offset:offset + size]
