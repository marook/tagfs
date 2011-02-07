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
import re
import datetime

projectdir = dirname(abspath(__file__))
reportdir = pjoin(projectdir, 'reports')
srcdir = pjoin(projectdir, 'src')
moddir = pjoin(srcdir, 'modules')
testdir = pjoin(projectdir, 'test')
testdatadir = pjoin(projectdir, 'etc', 'test', 'events')
testmntdir = pjoin(projectdir, 'mnt')

class Report(object):

    def __init__(self):
        self.reportDateTime = datetime.datetime.utcnow()
        self.reportDir = os.path.join(reportdir, self.reportDateTime.strftime('%Y-%m-%d_%H_%M_%S'))
        
        # fails when dir already exists which is nice
        os.makedirs(self.reportDir)

    @property
    def coverageReportFileName(self):
        return os.path.join(self.reportDir, 'coverage.txt')

def sourceFiles():
    yield os.path.join(srcdir, 'tagfs')
    
    sourceFilePattern = re.compile('^.*[.]py$')
    for root, dirs, files in os.walk(moddir):
        for f in files:
            if(not sourceFilePattern.match(f)):
                continue

            yield os.path.join(root, f)

class test(Command):
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        self._cwd = os.getcwd()
        self._verbosity = 2

    def finalize_options(self): pass

    def run(self):
        report = Report()

        testPyMatcher = re.compile('(.*/)?test[^/]*[.]py', re.IGNORECASE)

        tests = ['.'.join([
                basename(testdir), splitext(basename(f))[0]
        ]) for f in glob(pjoin(
                testdir, '*.py'
        )) if testPyMatcher.match(f)]

        print "..using:"
        print "  testdir:", testdir
        print "  testdatadir:", testdatadir
        print "  testmntdir:", testmntdir
        print "  tests:", tests
        print "  sys.path:", sys.path
        print
        sys.path.insert(0, moddir)
        sys.path.insert(0, srcdir)

        # configure logging
        # TODO not sure how to enable this... it's a bit complicate to enable
        # logging only for 'make mt' and disable it then for
        # 'python setup.py test'. 'python setup.py test' is such a gabber...
        #if 'DEBUG' in os.environ:
        #    from tagfs import log_config
        #    log_config.setUpLogging()

        suite = TestLoader().loadTestsFromNames(tests)
        r = TextTestRunner(verbosity = self._verbosity)

        def runTests():
            r.run(suite)

        try:
            import coverage

            c = coverage.coverage()
            c.start()
            runTests()
            c.stop()
    
            with open(report.coverageReportFileName, 'w') as reportFile:
                c.report([f for f in sourceFiles()], file = reportFile)

        except ImportError:
            print ''
            print 'coverage module not found.'
            print 'To view source coverage stats install http://nedbatchelder.com/code/coverage/'
            print ''

            runTests()


# Overrides default clean (which cleans from build runs)
# This clean should probably be hooked into that somehow.
class clean_pyc(Command):
    description = 'remove *.pyc files from source directory'
    user_options = []

    def initialize_options(self):
        self._delete = []
        for cwd, dirs, files in os.walk(projectdir):
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
    author_email = 'markus.pielmeier@gmx.de',
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
        (pjoin('share', 'doc', 'tagfs'), ['AUTHORS', 'COPYING', 'README'])
    ],
    scripts = [pjoin('src', 'tagfs')],
    packages = ['tagfs'],
    package_dir = {'': pjoin('src', 'modules')},
)
