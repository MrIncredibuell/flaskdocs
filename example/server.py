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
    response_schema=Schema({}),
    blueprint=blueprint,
)
def moo(animal="cow"):
    return jsonify({animal: "moo"})

app.register_blueprint(blueprint)


api.output_ts("example/ts")