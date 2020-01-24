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
@api.route(
    name="moo",
    path="/moo",
    methods=["GET", "POST"],
    body_schema=Schema({"animal": str}),
    response_schema=Schema({})
)
def moo(animal):
    return jsonify({animal: "moo"})


