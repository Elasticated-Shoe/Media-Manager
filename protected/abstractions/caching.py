from flask_caching import Cache
import protected.abstractions.globals as shared

def init(cache, app):
    cache.init_app(app)

def createCacheObject():
    return Cache(config={'CACHE_TYPE': 'simple'})

def getCacheByKey(theKey):
    cachedObject = shared.cache.get(theKey)
    if cachedObject:
        return cachedObject
    return False

def setCacheByKey(theKey, objectToCache):
    return shared.cache.set(theKey, objectToCache)

