#!/usr/bin/env python
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

import logging
import re

class TraceLogEntry(object):

    def __init__(self, context, path):
        self.context = context
        self.path = path

class TraceLog(object):

    LINE_BUFFER_SIZE = 100000

    TRACE_PATTERN = re.compile('[0-9\-,: ]+DEBUG (readlink|getattr|readdir) (.*)$')

    def __init__(self):
        self.entries = []

    def _readLogLine(self, line):
        m = TraceLog.TRACE_PATTERN.match(line)

        if not m:
            return

        context = m.group(1)
        path = m.group(2)

        self.entries.append(TraceLogEntry(context, path))

    def readLogFile(self, fileName):
        logging.info('Reading logfile ' + fileName)

        f = open(fileName)

        while True:
            lines = f.readlines(TraceLog.LINE_BUFFER_SIZE)
            if not lines:
                break;

            for line in lines:
                self._readLogLine(line)

class TraceResult(object):

    def __init__(self):
        self.contextHistogram = {}
        self.contextPathHistogram = {}

    def _analyzeContextHistogram(self, traceLog):
        for e in traceLog.entries:
            if not e.context in self.contextHistogram:
                self.contextHistogram[e.context] = 0

            self.contextHistogram[e.context] += 1

    def _analyzeContextPathHistogram(self, traceLog):
        for e in traceLog.entries:
            if not e.context in self.contextPathHistogram:
                self.contextPathHistogram[e.context] = {}

            ph = self.contextPathHistogram[e.context]

            if not e.path in ph:
                ph[e.path] = 0

            ph[e.path] += 1
            

    def _analyzeTraceLog(self, traceLog):
        self._analyzeContextHistogram(traceLog)
        self._analyzeContextPathHistogram(traceLog)

    def analyzeLogFile(self, fileName):
        tl = TraceLog()
        tl.readLogFile(fileName)

        self._analyzeTraceLog(tl)

def usage():
    # TODO print usage

    pass

def writeCSV(fileName, pathHistogram):
    import csv

    w = csv.writer(open(fileName, 'w'))
    
    for path, histogram in pathHistogram.iteritems():
        w.writerow([path, histogram])

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    import getopt
    import sys

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", [])
    except getopt.GetoptError:
        usage()

        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()

    tr = TraceResult()

    for fileName in args:
        tr.analyzeLogFile(fileName)

    print "Context Histogram"
    for context, calls in tr.contextHistogram.iteritems():
        print ' %s: %s' % (context, calls)

    for context, pathHistogram in tr.contextPathHistogram.iteritems():
        writeCSV('pathHistogram_' + context + '.csv', pathHistogram)
