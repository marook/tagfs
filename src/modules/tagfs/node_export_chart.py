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

from node_file import FileNode
import pylab
import cStringIO

class ChartImageNode(FileNode):

    def __init__(self, itemAccess, parentNode):
        self.itemAccess = itemAccess
        self.parentNode = parentNode

    @property
    def name(self):
        return 'chart.png'

    @property
    def items(self):
        return self.parentNode.items

    @property
    def content(self):
        pylab.clf()

        x = [0.0, 1.0, 2.0]
        y = [1.0, 2.0, 1.0]

        pylab.plot(x, y)

        out = cStringIO.StringIO()

        pylab.savefig(out, format = 'png')

        return out.getvalue()
