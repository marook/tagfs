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

import errno
import logging
import os
import stat
import unittest
import tagfs
import env
from tagfs import item_access
from tagfs import view

class TestView(unittest.TestCase):

    def validateDirectoryPath(self, view, path):
        # path is a directory

        # TODO implement propper offset handling
        for entry in view.readdir(path, 0):
            self.assertTrue(entry != None)

            # TODO put '.' and '..' in set
            if entry.name == '.':
                continue

            if entry.name == '..':
                continue

            self.validateView(view, path + '/' + entry.name)

    def validateLinkPath(self, view, path):
        l = view.readlink(path)

        self.assertNotEquals(-errno.ENOENT, l)

        self.assertTrue(len(l) > 0)

    def validateRegularFilePath(self, view, path):
        self.assertTrue(attr.st_size >= 0)

        self.assertTrue(view.open(path, 32768) == None)

        content = view.read(path, 4096, 0)

        self.assertNotEquals(-errno.ENOSYS, content)
        self.assertNotEquals(-errno.ENOENT, content)

        self.assertTrue(content != None)

        logging.debug('Content: ' + str(content))

        # TODO validate file close

        # TODO validate block file

    def validateView(self, view, path):
        attr = view.getattr(path)

        # assert every file belongs to 'me'
        # right now this is the default behaviour
        self.assertEquals(os.getuid(), attr.st_uid)
        self.assertEquals(os.getgid(), attr.st_gid)

        self.assertNotEquals(-errno.ENOSYS, attr,
                              msg = 'Expected attributes for path ' + path + ' but was ' + str(attr))
        self.assertNotEquals(-errno.ENOENT, attr,
                              msg = 'Expected attributes for path ' + path + ' but was ' + str(attr))

        if (attr.st_mode & stat.S_IFDIR == stat.S_IFDIR):
            self.validateDirectoryPath(view, path)
        elif (attr.st_mode & stat.S_IFLNK == stat.S_IFLNK):
            self.validateLinkPath(view, path)
        elif (attr.st_mode & stat.S_IFREG == stat.S_IFREG):
            self.validateRegularFilePath(view, path)
        else:
            self.fail('Unknown attributes ' + str(attr))

    @property
    def configs(self):
        for enableValueFilters in (True, False):
            for enableRootItemLinks in (True, False):
                yield tagfs.Config(enableValueFilters, enableRootItemLinks)

    @property
    def itemAccesses(self):
        yield item_access.ItemAccess(os.path.join(env.projectdir, 'etc', 'test', 'events'),
                                     '.tag')

        yield item_access.ItemAccess(os.path.join(env.projectdir, 'etc', 'demo', 'events'),
                                     '.tag')
            

    def testView(self):
        for conf in self.configs:
            for itemAccess in self.itemAccesses:
                try:
                    v = view.View(itemAccess, conf)

                    self.validateView(v, '/')
                except Exception as e:
                    raise Exception('Can\' test view for conf %s and itemAccess %s.' % (conf, itemAccess), e)
                

if __name__ == "__main__":
    unittest.main()
