from flask import render_template, request, redirect, session
import protected.globals as shared

@shared.cache.cached(key_prefix='login') # Decorator caches the dashboard html PERMANENTLY
def renderLogin():
    print("Cache Not Used")
    return render_template('login.html', pageHead="Login Page")

def check():
    if "sessionStatus" not in session or session["sessionStatus"] != "loggedIn":
        if "static" not in request.base_url:
            return False
    return True

def init():
    if request.method == 'GET':
        return renderLogin()
    elif request.method == 'POST':
        userPassword = request.form["password"]
        username = request.form["username"]
        if userPassword ==  "admin" and username == "admin":
            session["sessionStatus"] = "loggedIn"
            return redirect("", code=307)
        return renderLogin()
    else:
        print(request.method)
        print("why")
        return 405