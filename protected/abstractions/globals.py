from flask_caching import Cache
import configparser
import os

# Cache Should only be created once, then all should use this same object
cache = Cache(config={'CACHE_TYPE': 'simple'})

# Create config object
config = configparser.ConfigParser() # Initialise the config parser
configFile = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'config.ini'))
config.read(configFile) # Read the config file
globalSettings = {}
for section in config: # map from file to object
    globalSettings[section] = {}
    globalSettings[section] = config[section]