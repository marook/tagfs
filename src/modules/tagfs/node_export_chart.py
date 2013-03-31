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
#

from cache import cache
from node_file import FileNode
import pylab
import cStringIO

class ChartImageNode(FileNode):

    def __init__(self, itemAccess, parentNode, context):
        self.itemAccess = itemAccess
        self.parentNode = parentNode
        self.context = context

    @property
    def name(self):
        return 'chart-%s.png' % (self.context,)

    @property
    def items(self):
        return self.parentNode.items

    @property
    @cache
    def content(self):
        pylab.clf()

        xValues = []
        yValues = []

        for x, item in enumerate(self.items):
            for tag in item.tags:
                c = tag.context

                if(c != self.context):
                    continue

                try:
                    y = float(tag.value)
                except:
                    y = None

                if(y is None):
                    try:
                        # some love for our german people
                        y = float(tag.value.replace(',', '.'))
                    except:
                        continue

                xValues.append(x)
                yValues.append(y)

        pylab.plot(xValues, yValues, label = self.context)

        out = cStringIO.StringIO()

        pylab.savefig(out, format = 'png')

        return out.getvalue()
