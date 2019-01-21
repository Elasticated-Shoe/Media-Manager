from flask_caching import Cache

# Cache Should only be created once, then all should use this same object
cache = Cache(config={'CACHE_TYPE': 'simple'})