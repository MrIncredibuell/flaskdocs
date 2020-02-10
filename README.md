__flaskdocs__ is a lightweight wrapper around a flask app which aims to centralize both validation and documentation of an API.  Declare the schemas you're accept/return, and flaskdocs will let you generate an openapi.json file, as well as validating incoming requests and returning errors to the client if a request doesn't match the given schema.

# Example usage:

Declare a flask app and pass it to a flaskdocs API as follows:

    from flask import Flask, jsonify

    from flaskdocs import API
    from flaskdocs.schema import (
        JsonSchema,
        QueryParameterSchema,
        Literal,
        Use,
    )

    app = Flask(__name__)

    api = API(
        title="example",
        version="0.0.1",
        description="Here's an example API",
        app=app,
    )

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
    )
    def add(x: float, y: float):
        return jsonify({"sum": x + y})

    api.output_openapi("example/openapi-spec.json")

To run a more complete example (found in the `example` folder) run `FLASK_APP=example/server.py python -m flask run` from this directory.