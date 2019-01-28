from flask_caching import Cache
import configparser

# Cache Should only be created once, then all should use this same object
cache = Cache(config={'CACHE_TYPE': 'simple'})

# Create config object
config = configparser.ConfigParser() # Initialise the config parser
config.read("protected/config.ini") # Read the config file
globalSettings = {}
for section in config: # map from file to object
    globalSettings[section] = {}
    globalSettings[section] = config[section]