#
# Copyright 2009, 2010 Markus Pielmeier
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

prefix = /usr/local
bindir = $(prefix)/bin
docdir = $(prefix)/share/doc/tagfs
installdirs = $(bindir) $(docdir)

srcdir = .
targetdir = $(srcdir)/target

testdatadir = $(srcdir)/etc/test/events
testmntdir = $(shell pwd)/mnt

pymoddir = $(srcdir)/src/modules

PYTHON = python
INSTALL = install
INSTALL_DATA = $(INSTALL) -m 644
INSTALL_PROGRAM = $(INSTALL)

DOCS = AUTHORS COPYING README VERSION

VERSION = `cat VERSION`
TSTAMP = `date '+%Y%m%d_%H%M'`

.PHONY: all
all:
	@echo "42. That's all."
	@echo "Try 'make mounttest' for something more interesting."

.PHONY: clean
clean:
	find $(srcdir) -name '*.pyc' -type f -exec rm {} \;
	@if test "`mount | grep -e 'tagfs.*on.*$(testmntdir)'`"; then \
		echo "tagfs mounted on '$(testmntdir)' -- keeping it."; \
	elif test -d '$(testmntdir)'; then \
		echo 'removing $(testmntdir)'; \
		rmdir '$(testmntdir)'; \
	fi

	rm -r -- "$(targetdir)"

.PHONY: test
test:
	$(PYTHON) $(srcdir)/test/test_all.py

$(installdirs):
	$(INSTALL) -d $(installdirs)

.PHONY: install
install: $(installdirs)
	$(INSTALL_PROGRAM) $(srcdir)/src/tagfs $(bindir)/tagfs
	$(INSTALL_DATA) $(DOCS) $(docdir)

.PHONY: uninstall
uninstall:
	rm -- $(bindir)/tagfs
	rm -r -- $(docdir)

$(testmntdir):
	mkdir -p $@

.PHONY: mounttest
mounttest: $(testmntdir)
	PYTHONPATH=$(pymoddir):$(PYTHONPATH) \
		$(PYTHON) $(srcdir)/src/bin/tagfs -i $(testdatadir) $(testmntdir)

.PHONY: unmounttest
unmounttest:
	fusermount -u $(testmntdir)
	rmdir -- $(testmntdir)

.PHONY: umounttest
umounttest: unmounttest

.PHONY: mt
mt: mounttest

.PHONY: umt
umt: unmounttest

.PHONY: distsnapshot
distsnapshot:
	mkdir -p -- "$(targetdir)/tagfs_$(VERSION)_snapshot_$(TSTAMP)"

	cp -a $(DOCS) etc src test util setup.py README.dev Makefile "$(targetdir)/tagfs_$(VERSION)_snapshot_$(TSTAMP)"

	tar cjf $(targetdir)/tagfs_$(VERSION)_snapshot_$(TSTAMP)-src.tar.bz2 '--exclude=*~' '--exclude=*.pyc' -C "$(targetdir)" "tagfs_$(VERSION)_snapshot_$(TSTAMP)"
