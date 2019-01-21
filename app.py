from flask import Flask
from flask_caching import Cache
import protected.globals as shared
import protected.dashboardController as dashController
import protected.loginController as loginController
import protected.noPageController as pageNotFoundController

app = Flask(__name__, template_folder='protected/views')
app.config['SECRET_KEY'] = shared.globalSettings["flask"]["key"]
shared.cache.init_app(app)

@app.before_request
def runPreCheck():
    if loginController.check() == False:
        return loginController.init()

@app.route('/', methods=["POST", "GET"])
def index():
    return dashController.renderDashboard()

@app.errorhandler(404)
def pageNotFound(e):
    return pageNotFoundController.render404()

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port = 5006, threaded=True)