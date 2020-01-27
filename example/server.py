from flask import Blueprint, render_template, abort, Flask, jsonify, request
from jinja2 import TemplateNotFound

from flaskdocs import API, Route, Schema

app = Flask(__name__)

api = API(
    name="example",
    app=app,
)

blueprint = Blueprint('example', __name__)


@api.route(
    name="moo",
    path="/moo",
    methods=["GET", "POST"],
    body_schema=Schema({"animal": str}),
    response_schema=Schema({"moo": str}),
    blueprint=blueprint,
)
def moo(animal="cow"):
    return jsonify({"moo": animal})

@api.route(
    name="hello",
    path="/hello",
    methods=["POST"],
    body_schema=Schema({"name": str}),
    response_schema=Schema({"greeting": str}),
    blueprint=blueprint,
)
def hello(name="sir"):
    return jsonify({"greeting": f"hello {name}"})


app.register_blueprint(blueprint)


api.output_ts("example/ts")