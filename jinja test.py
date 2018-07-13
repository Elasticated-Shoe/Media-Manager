from flask import Flask
from flask import render_template as flask_render
from jinja2 import Environment, PackageLoader, FileSystemLoader

TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader("templates"), trim_blocks=False)
#TEMPLATE_ENVIRONMENT = Environment(loader=PackageLoader('yourapplication', 'templates'),autoescape=select_autoescape(['html', 'xml']))
#TEMPLATE_ENVIRONMENT = FileSystemLoader('/templates')

def html_interface():
    app = Flask(__name__)


    @app.route('/')
    def serve_page():
        print("placeholder")
        return flask_render("output.html")

    if __name__ == '__main__':
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def create_index_html():
    fname = "templates/output.html"
    urls = ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
    context = {
        'urls': urls
    }
    #
    with open(fname, 'w') as f:
        html = render_template('index.html', context)
        f.write(html)

create_index_html()
html_interface()
#h = threading.Thread(target=html_interface)
#h.start()