from flask import render_template, request, redirect, session
import protected.abstractions.globals as shared

def init():
    """
        If the request method is a get, serve the user the login page, otherwise the user must be posting the login details. 
    """
    if request.method == 'GET':
        return renderLogin()
    elif request.method == 'POST':
        userPassword = request.form["password"]
        username = request.form["username"]
        if userPassword ==  "admin" and username == "admin":
            session["sessionStatus"] = "loggedIn"
            session["settingsAccess"] = 1
            return redirect("", code=307)
        return renderLogin()
    else:
        print(request.method)
        print("why")
        return "405"

@shared.cache.cached(key_prefix='login') # Decorator caches the dashboard html PERMANENTLY
def renderLogin():
    print("RenderLogin, Cache Not Used")
    return render_template('login.html', pageHead="Login Page")

def check():
    if "sessionStatus" not in session or session["sessionStatus"] != "loggedIn":
        if "static" not in request.base_url:
            return False
    return True