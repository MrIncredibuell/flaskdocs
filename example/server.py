from flask import Blueprint, render_template, abort, Flask, jsonify, request
from jinja2 import TemplateNotFound

from flaskdocs import API, Route
from flaskdocs.schema import JsonSchema, QueryParametersSchema, Optional, Literal, Use

app = Flask(__name__)

api = API(
    title="example",
    version="0.0.1",
    description="Here's an example API",
    app=app,
)

blueprint = Blueprint('example', __name__)

@api.route(
    name="Add Numbers",
    path="/add",
    methods=["GET"],
    description="Add two numbers together and return the sum",
    query_parameter_schema=QueryParametersSchema({
        # use "Use" here to tell the parser try calling float, rather
        # than doing a type check, because queryParameters always come
        # in as strings
        Literal("x", description="The first number to add"): Use(float),
        Literal("y", description="The second number to add"): Use(float),
    }),
    response_schema={200: JsonSchema({
        Literal("sum", description="The sum x + y"): float
    })},
    blueprint=blueprint,
)
def add(x: float, y: float):
    return jsonify({"sum": x + y})

@api.route(
    name="Say Hello",
    path="/hello",
    methods=["POST"],
    description="Say hello to the given name",
    body_schema=JsonSchema({
        Literal("name", description="The name of the person to greet"): str
    }),
    response_schema={200: JsonSchema({
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