#
# Copyright 2009 Markus Pielmeier
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

BIN = /usr/local/bin
DOC = /usr/local/share/doc/tagfs

all:

clean:
	find src -name '*.pyc' -type f -exec rm {} \;
	find test -name '*.pyc' -type f -exec rm {} \;

install:
	install -d $(BIN) $(DOC)
	install -T src/tagfs.py $(BIN)/tagfs
	cp -a AUTHORS COPYING README $(DOC)

uninstall:
	rm -- $(BIN)/tagfs
	rm -r -- $(DOC)
