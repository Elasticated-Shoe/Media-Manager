from flask import Flask, render_template

app = Flask(__name__, template_folder='protected/views')

@app.route('/')
def index():
    return render_template('dashboard.html', pageHead="Dashboard")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port = 5006, threaded=True)