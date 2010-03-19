#!/usr/bin/env python
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

import time
import functools

class NoCacheStrategy(object):
    """This cache strategy reloads the cache on every call.
    """
    
    def isCacheValid(self, f, *args, **kwargs):
        return False
    
class NoReloadStrategy(object):
    """This cache strategy never reloads the cache.
    """
    
    def isCacheValid(self, f, *args, **kwargs):
        return True

class TimeoutReloadStrategy(object):
    
    def __init__(self, timeoutDuration = 10 * 60):
        self.timeoutDuration = timeoutDuration
    
    def isCacheValid(self, f, *args, **kwargs):
        obj = args[0]
        
        timestampFieldName = '__' + f.__name__ + 'Timestamp'
        now = time.time()
    
        if not hasattr(obj, timestampFieldName):
            setattr(obj, timestampFieldName, now)
        
            return False
    
        lastTime = getattr(obj, timestampFieldName)
    
        if now - lastTime < self.timeoutDuration:
            return True
    
        setattr(obj, timestampFieldName, now)
    
        return False


def cache(f, reloadStrategy = NoReloadStrategy()):
    """This annotation is used to cache the result of a method call.
    
    @param f: This is the wrapped function which's return value will be cached.
    @param reload: This is the reload strategy. This function returns True when
    the cache should be reloaded. Otherwise False.
    @attention: The cache is never deleted. The first call initializes the
    cache. The method's parameters just passed to the called method. The cache
    is not evaluating the parameters.
    """
    
    @functools.wraps(f)
    def cacher(*args, **kwargs):
        obj = args[0]
        
        cacheMemberName = '__' + f.__name__ + 'Cache'
        
        # the reload(...) call has to be first as we always have to call the
        # method. not only when there is a cache member available in the object.
        if (not reloadStrategy.isCacheValid(f, *args, **kwargs)) or (not hasattr(obj, cacheMemberName)):
            value = f(*args, **kwargs)
            
            setattr(obj, cacheMemberName, value)
            
            return value
            
        return getattr(obj, cacheMemberName)
    
    return cacher

