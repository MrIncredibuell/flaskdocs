from flask import Blueprint, render_template, abort, Flask, jsonify, request
from jinja2 import TemplateNotFound

from flaskdocs import API, Route, Schema

app = Flask(__name__)

api = API(
    name="example",
    app=app,
)

simple_page = Blueprint('simple_page', __name__,
                        template_folder='templates')

# @simple_page.route('/', defaults={'page': 'index'})
def moo(animal):
    return jsonify({animal: "moo"})

@simple_page.route("/moo", methods=["POST"])
def handler(*args, **kwargs):
    return Route(
        name="moo",
        path="/moo",
        func=moo,
        body_schema=Schema({"animal": str}),
        response_schema=Schema({})
    ).handler(*args, **kwargs)


app.register_blueprint(simple_page)

