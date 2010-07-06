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

import functools
import logging

def logCall(f):

    @functools.wraps(f)
    def logCall(*args, **kwargs):
        o = args[0]

        logger = logging.getLogger(o.__class__.__name__)
        logger.debug(f.__name__ + '(' + (', '.join('\'' + str(a) + '\'' for a in args[1:])) + ')')

        return f(*args, **kwargs)

    return logCall
