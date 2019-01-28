from flask import render_template, request, session
import protected.abstractions.globals as shared
import protected.abstractions.fileOperations as fileOp
import protected.abstractions.mediaAPIs as metadata
import protected.abstractions.caching as cacheAb

def init():
    if request.method == "POST":
        return renderDashboard()
    if request.query_string == b'':
        return renderDashboard()
    else:
        if session["settingsAccess"] == 1:
            userAction = request.args.get('Action')
            if userAction:
                if userAction == "refreshMeta":
                    fetchMeta(request.args.get('Force'))
            return "200"
        return "403"

@shared.cache.cached(key_prefix='dashboard') # Decorator caches the dashboard html PERMANENTLY
def renderDashboard():
    print("Dashboard, Cache Not Used")
    return render_template('dashboard.html', pageHead="Dashboard")

def fetchMeta(refreshAll = False):
    filesByType = fileOp.getFileList({
        "film": [r"S:\GIT Repos\Media-Manager\testdir\film"],
        "tv": [r"S:\GIT Repos\Media-Manager\testdir\tv"]
    })
    for fileTypes in filesByType:
        if fileTypes in ["film"]:
            for mediaItem in filesByType[fileTypes]:
                if filesByType[fileTypes][mediaItem][0]["metadata"] == {} or refreshAll == True:
                    filesByType[fileTypes][mediaItem][0]["metadata"] = metadata.fetchFilmData(mediaItem) # calling api to fetch metadata
    cacheAb.setCacheByKey("media", filesByType)
