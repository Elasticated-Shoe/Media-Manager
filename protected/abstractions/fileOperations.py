import os
import protected.abstractions.globals as shared
import protected.abstractions.caching as cacheAb
#import caching as cacheAb
#import globals as shared

def getFileList(dictTypeDirList, refreshCache = False):
    """
        This function gets a list of the files in the provided directories. To do this a dictionary formatted like {"mediaType": ["dir1", "dir2"], "mediaType2": ["dir3", "dir4"]}
        If the object is already found in the cache than it will return that instead of generating it by default. If True is passed into the second argument this behaviour
        will be overridden.
    """
    objectCache = cacheAb.getCacheByKey("media")
    if objectCache != False and refreshCache == False:
        return objectCache
    mediaCache = {}
    videoFormats = ["mkv", "mp4", "mov"] # specify later
    # would list comprehension really be much faster here, does this even need to be fast?
    for fileType in dictTypeDirList:
        mediaCache[fileType] = {}
        for directories in dictTypeDirList[fileType]:
            for directoryBase, dirs, allFiles in os.walk(directories):
                for fileName in allFiles:
                    if fileName.split(".")[-1] not in videoFormats:
                        continue
                    fullFilePath = os.path.join(directoryBase, fileName)
                    fileName = fileName.replace(fileName.split(".")[-1], "")
                    if fileName not in mediaCache[fileType]:
                        mediaCache[fileType][fileName] = []
                    mediaCache[fileType][fileName].append({
                        "path": fullFilePath,
                        "metadata": {}
                    })
    cacheAb.setCacheByKey("media", mediaCache) # could check if true, does it fail often?
    return mediaCache