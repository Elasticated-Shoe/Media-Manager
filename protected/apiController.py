from flask import render_template, request, session

def init():
    if request.method == "GET" and request.query_string == b'':
        if session["settingsAccess"] == 1:
            print(request.query_string)
        else:
            return "403"