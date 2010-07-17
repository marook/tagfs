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

import sys

def setupenv():
    from os.path import dirname, abspath, exists, join as pjoin, split as psplit

    global eventsdir
    global projectdir
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
