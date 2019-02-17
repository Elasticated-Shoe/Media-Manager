from flask import Flask
import protected.abstractions.globals as shared
import protected.abstractions.caching as cacheAb

app = Flask(__name__, template_folder='protected/views') # create flask app object, specify different folder for templates

app.config['SECRET_KEY'] = shared.globalSettings["flask"]["key"] # read secret key from config file
cacheAb.init(shared.cache, app) # initiate the cache

@app.before_request # before every request, except ones to the static folder, check user is logged in
def runPreCheck():
    import protected.loginController as loginController
    if loginController.check() == False:
        return loginController.init()

@app.route('/', methods=["POST", "GET"]) # return main page
def index():
    import protected.dashboardController as dashController
    return dashController.init()

@app.errorhandler(404) # 404 error handler
def pageNotFound(e):
    import protected.noPageController as pageNotFoundController
    return pageNotFoundController.render404()

if __name__ == '__main__':
    import protected.abstractions.prepare as initial
    initial.startUp()
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port = 5006, threaded=True)