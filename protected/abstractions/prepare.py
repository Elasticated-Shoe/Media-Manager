import os
import subprocess

def runCommand(command):
    openCommandHandle = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = openCommandHandle.communicate()
    return output

def allFilesNoRecurse(directory, extension):
    bundleFile = os.path.join(directory, "bundle" + extension)
    fileToEdit = open(bundleFile, "w", encoding="utf-8")
    fileToEdit.write("")
    for fileName in os.listdir(directory):
        if "bundle" in fileName or "tempfile" in fileName:
            continue
        tempFullPath = os.path.join(directory, fileName)
        if extension == ".js":
            runCommand(r'uglifyjs "' + tempFullPath + '"' + ' -o ' + '"' + os.path.join(directory, "tempfile.js") + '"')
            tempFullPath = os.path.join(directory, "tempfile.js")
        if extension == ".css":
            runCommand(r'uglifycss "' + tempFullPath + '"' + ' --output ' + '"' + os.path.join(directory, "tempfile.css") + '"')
            tempFullPath = os.path.join(directory, "tempfile.css")
        f = open(tempFullPath, "r")
        with open(bundleFile, "a") as fileToAppend:
            fileToAppend.write(f.read())

def startUp():
    print("Starting Up The App, Building The App")
    cssFiles = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', "static", "css"))
    jsFiles = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', "static", "js", "vendor"))
    allFilesNoRecurse(cssFiles, ".css")
    allFilesNoRecurse(jsFiles, ".js")
    print("Finished Build")