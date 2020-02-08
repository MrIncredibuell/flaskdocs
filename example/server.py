from flask import Blueprint, render_template, abort, Flask, jsonify, request
from jinja2 import TemplateNotFound

from flaskdocs import API, Route
from flaskdocs.schema import (
    JsonSchema,
    QueryParameterSchema,
    UrlParameterSchema,
    Optional,
    Literal,
    Use,
    And,
    SchemaError,
)

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
    query_parameter_schema=QueryParameterSchema({
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
        Optional(
            "name",
            description="The name of the person to greet",
            default="sir"): str
    }),
    response_schema={200: JsonSchema({
        Literal(
            "greeting",
            description="A personalized greeting for the person",
        ): str,
    })},
    blueprint=blueprint,
)
def hello(name="sir"):
    return jsonify({"greeting": f"hello {name}"})


@api.route(
    name="Echo",
    path="/echo/<value>",
    methods=["GET"],
    description="Echo back the url parameter",
    url_parameter_schema=UrlParameterSchema({
        Literal("value", description="The value to echo"): str
    }),
    response_schema={200: JsonSchema({
        Literal(
            "value",
            description="A same value given",
        ): str,
    })},
    blueprint=blueprint,
)
def echo(value):
    return jsonify({"value": value})


# Helper functions for more complex schema validation
def min_len(length):
    """
    Return function to check if the length is more than
    a given length
    """
    def f(value):
        if len(value) < length:
            raise SchemaError(f"Length of '{value}' is less than {length}")
        return True
    return f

def is_email(value):
    """
    Simple validation to check if an string contains an '@'
    and has both a user and hostname component
    """
    if value.count('@') != 1:
        raise SchemaError(f"'{value}' must contain exactly one '@'")

    # @ should not be the first or last character
    index = value.index('@')
    if index == 0:
        raise SchemaError(f"'{value}' must contain a user component")
    if index == len(value) - 1:
        raise SchemaError(f"'{value}' must contain a hostname component")
    return True

USER_SCHEMA = {
    Literal(
        "name",
        description="The user's name",
    ): And(
        str,
        min_len(1),
    ),
    Literal(
        "email",
        description="The user's email address",
    ): And(
        str,
        min_len(1),
        is_email,
    ),
}

@api.route(
    name="Create User",
    path="/users",
    methods=["PUT"],
    description="Create the given user",
    body_schema=JsonSchema({
        Literal("user", description="The user to create"): USER_SCHEMA,
    }),
    response_schema={200: JsonSchema({
        Literal("user", description="The created user"): USER_SCHEMA,
    })},
    blueprint=blueprint,
)
def create_user(user):
    return jsonify({"user": user})

app.register_blueprint(blueprint)

api.output_ts("example/ts")
api.output_openapi("example/openapi-spec.json")