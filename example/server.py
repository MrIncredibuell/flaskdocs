from flask import Blueprint, render_template, abort, Flask, jsonify, request
from jinja2 import TemplateNotFound

from flaskdocs import API, Route
from flaskdocs.schema import Schema, Optional, Literal

app = Flask(__name__)

api = API(
    title="example",
    version="0.0.1",
    description="Here's an example API",
    app=app,
)

blueprint = Blueprint('example', __name__)

@api.route(
    name="moo",
    path="/moo",
    methods=["POST"],
    body_schema=Schema({
        Literal("animal", description="An animal, for some reason"): str,
    }),
    response_schema={200: Schema({
        Literal("moo", description="The animal which was passed in"): str
    })},
    blueprint=blueprint,
)
def moo(animal="cow"):
    return jsonify({"moo": animal})

@api.route(
    name="hello",
    path="/hello",
    methods=["POST"],
    body_schema=Schema({
        Literal("name", description="The name of the person to greet"): str
    }),
    response_schema={200: Schema({
        Optional(
            "greeting",
            description="A personalized greeting for the person",
            default="sir",
        ): str,
    })},
    blueprint=blueprint,
)
def hello(name="sir"):
    return jsonify({"greeting": f"hello {name}"})

app.register_blueprint(blueprint)

api.output_ts("example/ts")
api.output_openapi("example/openapi-spec.json")