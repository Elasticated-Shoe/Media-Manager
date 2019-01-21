from flask import Flask, session
from flask_caching import Cache
import protected.globals as shared
import protected.dashboardController as dashController

app = Flask(__name__, template_folder='protected/views')
app.config['SECRET_KEY'] = shared.globalSettings["flask"]["key"]
shared.cache.init_app(app)

@app.before_request
def runPreCheck():
    if "sessionStatus" not in session or session["sessionStatus"] != "loggedIn":
        return "Not Logged In"

@app.route('/')
def index():
    return dashController.renderDashboard()

@app.errorhandler(404)
def pageNotFound(e):
    return "True"
    #return render_template('404.html', pageHead="Page Not Found"), 404

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port = 5006, threaded=True)