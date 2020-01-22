from flask import Blueprint, render_template, abort, Flask, Response
from jinja2 import TemplateNotFound

from flaskdocs import API

app = Flask(__name__)

api = API()

simple_page = Blueprint('simple_page', __name__,
                        template_folder='templates')

@simple_page.route('/', defaults={'page': 'index'})
@simple_page.route('/<page>')
def show(page):
    try:
        return Response("moo")
    except TemplateNotFound:
        abort(404)


app.register_blueprint(simple_page)

