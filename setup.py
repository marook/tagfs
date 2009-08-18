#!/usr/bin/env python
#
# Copyright 2009 Peter Prohaska
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

from distutils.core import setup, Command
import sys
import os
from os.path import (
        basename,
        dirname,
        abspath,
        splitext,
        join as pjoin
)
from glob import glob
from unittest import TestLoader, TextTestRunner

srcdir = dirname(abspath(__file__))

testdir = pjoin(srcdir, 'test')
testdatadir = pjoin(srcdir, 'etc/test/events/')
testmntdir = pjoin(srcdir, 'mnt')

class test(Command):
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        self._cwd = os.getcwd()
        self._verbosity = 2

    def finalize_options(self): pass

    def run(self):
        tests = ['.'.join([
                basename(testdir), splitext(basename(f))[0]
        ]) for f in glob(pjoin(
                testdir, '*.py'
        )) if not f.endswith('__init__.py')]

        sys.path.append(pjoin(srcdir, 'src'))

        suite = TestLoader().loadTestsFromNames(tests)
        TextTestRunner(verbosity=self._verbosity).run(suite)


# Overrides default clean (which cleans from build runs)
# This clean should probably be hooked into that somehow.
class clean_pyc(Command):
    description = 'remove *.pyc files from source directory'
    user_options = []

    def initialize_options(self):
        self._delete = []
        for cwd, dirs, files in os.walk(srcdir):
            self._delete.extend(
                pjoin(cwd, f) for f in files if f.endswith('.pyc')
            )

    def finalize_options(self): pass

    def run(self):
        for f in self._delete:
            try:
                os.unlink(f)
            except OSError, e:
                print "Strange '%s': %s" % (f, e)
                # Could be a directory.
                # Can we detect file in use errors or are they OSErrors
                # as well?
                # Shall we catch all?

setup(
    cmdclass = {
        'test': test,
        'clean_pyc': clean_pyc,
    },
    name = 'tagfs',
    version = '0.1',
    url = 'http://wiki.github.com/marook/tagfs',
    description = '',
    long_description = '',
    author = 'Markus Pielmeier',
    author_email = '',
    license = 'GPLv3',
    download_url = 'http://github.com/marook/tagfs/downloads/tagfs_0.1-src.tar.bz2',
    platforms = 'Linux',
    requires = [],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Filesystems'
    ],
    data_files = [
        ('share/doc/tagfs', ['AUTHORS', 'COPYING', 'README'])
    ],
    scripts = ['tagfs'],
)
