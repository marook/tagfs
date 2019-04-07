tagfs - tag file system

1) Introduction
2) Requirements
3) Installation
4) Tagging Files
5) Usage
6) Configuration
6.1) Options
6.1.1) tagFileName
6.1.2) enableValueFilters
6.1.3) enableRootItemLinks
7) Freebase Integration
8) Bugs
9) Further Reading
10) Contact


---------------------------------------------------------------------
Introduction

tagfs is used to organize your files using tags.

This document contains basic usage instructions for users. To develop or debug
tagfs see the README.dev file.


---------------------------------------------------------------------
Requirements

* python 2.5, 2.6, 2.7
* Linux kernel with fuse enabled
* python-fuse installed
* python-matplotlib


---------------------------------------------------------------------
Installation

To install tagfs into your home directory type the following:

$ python setup.py test e2e_test install --home ~/.local

If you haven't already extended your local python path then add the following
to your environment configuration script. For example to your ~/.bashrc:

$ export PYTHONPATH=~/.local/lib/python:$PYTHONPATH

You may also need to add ~/.local/bin to your PATH environment variable:

$ export PATH=~/.local/bin:$PATH


---------------------------------------------------------------------
Tagging Files

Before you can filter anything using tagfs you need to tag your items. An item
is a directory which contains a file called .tag. All items must be below one
directory.

Let's create a simple item structure.

First we create the root directory for all items:
$ mkdir items

Then we create our first item:
$ mkdir items/Ted

We tag the 'Ted' item as movie:
$ echo movie >> items/Ted/.tag

We also tag 'Ted' as genre comedy:
$ echo 'genre: comedy' >> items/Ted/.tag

Then we add a second item:
$ mkdir items/banana
$ echo fruit >> items/banana/.tag
$ echo 'genre: delicious' >> items/banana/.tag

Modifying .tag files using echo, grep, sed may be a little hard sometimes.
There are some convenience scripts available through the tagfs-utils project.
See https://github.com/marook/tagfs-utils for details.


---------------------------------------------------------------------
Usage

After installation tagfs can be started the following way.

Mount a tagged directory:
$ tagfs -i /path/to/my/items/directory /path/to/my/mount/point

Unmount a tagged directory: 
$ fusermount -u /path/to/my/mount/point

Right now tagfs reads the taggings only when it's getting mounted. So if you
modify the tags after mounting you will not see any changes in the tagfs file
system.

In general tagfs will try to reduce the number of filter directories below the
virtual file system. That's why you may not see some filters which would not
reduce the number of selected items.


---------------------------------------------------------------------
Configuration

tagfs can be configured through configuration files. Configuration files are
searched in different locations by tagfs. The following locations are used.
Locations with higher priority come first:
- <items directory>/.tagfs/tagfs.conf
- ~/.tagfs/tagfs.conf
- /etc/tagfs/tagfs.conf

Right now the following configuration options are supported.


---------------------------------------------------------------------
Configuration - Options - tagFileName

Through this option the name of the parsed tag files can be specified. The
default value is '.tag'.

Example:

[global]
tagFileName = ABOUT


---------------------------------------------------------------------
Configuration - Options - enableValueFilters

You can enable or disable value filters. If you enable value filters you will
see filter directories for each tag value. For value filters the tag's
context can be anyone. The default value is 'false'.

Example:

[global]
enableValueFilters = true


---------------------------------------------------------------------
Configuration - Options - enableRootItemLinks

To show links to all items in the tagfs '/' directory enable this option. The
default value is 'false'.

Example:

[global]
enableRootItemLinks = true


---------------------------------------------------------------------
Freebase Integration

Freebase is an open graph of people, places and things. See
http://www.freebase.com/ for details. tagfs allows you to extend your own
taggings with data directly from the freebase graph.

WARNING! Freebase support is currently experimental. It is very likely that the
freebase syntax within the .tag files will change in future releases of tagfs.

In order to use freebase you need to install the freebase-python bindings. They
are available via https://code.google.com/p/freebase-python/

To extend an item's taggings with freebase data you have to add a freebase query
to the item's .tag file. Here's an example:

_freebase: {"id": "/m/0clpml", "type": "/fictional_universe/fictional_character", "name": null, "occupation": null}

tagfs uses the freebase MQL query format which is described below the following
link http://wiki.freebase.com/wiki/MQL

The query properties with null values are added as context/tag pairs to the
.tag file's item.

Generic freebase mappings for all items can be specified in the file
'<items directory>/.tagfs/freebase'. Every line is one freebase query. You can
reference tagged values via the '$' operator. Here's an example MQL query with
some demo .tag files:

<items directory>/.tagfs/freebase:
{"type": "/film/film", "name": "$name", "genre": null, "directed_by": null}

<items directory>/Ted/.tag:
name: Ted

<items directory>/Family Guy/.tag:
name: Family Guy

When mounting this example the genre and director will be fetched from freebase
and made available as filtering directories.


---------------------------------------------------------------------
Bugs

Viewing existing and reporting new bugs can be done via the github issue
tracker:
https://github.com/marook/tagfs/issues


---------------------------------------------------------------------
Further Reading

Using a file system for my bank account (Markus Pielmeier)
http://pielmeier.blogspot.com/2010/08/using-file-system-for-my-bank-account.html


---------------------------------------------------------------------
Contact

* homepage: http://wiki.github.com/marook/tagfs
* author: Markus Peröbner <markus.peroebner@gmail.com>
