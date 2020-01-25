from typing import List, Callable
from .schema import Schema, SchemaError
from flask import Flask, request, jsonify
import warnings

class API:
    def __init__(
            self,
            name: str,
            app: Flask,
            description: str = None,
    ):
        self.app = app
        self.name = name
        self.routes = {}

    def add_route(
            self,
            func,
            path,
            name=None,
            methods=None,
            query_parameter_schema: Schema=None,
            body_schema: Schema=None,
            response_schema: Schema=None,
    ):

        route = Route(
            func=func,
            name=name,
            path=path,
            methods=methods,
            query_parameter_schema=query_parameter_schema,
            body_schema=body_schema,
            response_schema=response_schema,
        )

        self.routes[name] = route

        self.app.add_url_rule(
            path,
            name,
            view_func=route.handler,
            methods=methods,
        )

    def route(
        self,
        path,
        name=None,
        methods=None,
        query_parameter_schema: Schema=None,
        body_schema: Schema=None,
        response_schema: Schema = None,
    ):
        def wrapper(func):
            self.add_route(
                func=func,
                name=name,
                path=path,
                methods=methods,
                query_parameter_schema=query_parameter_schema,
                body_schema=body_schema,
                response_schema=response_schema,
            )
        return wrapper

    def describe(self):
        return ""

class Route:
    def __init__(
        self,
        name: str,
        path: str,
        methods: str,
        func: Callable,
        query_parameter_schema: Schema=None,
        body_schema: Schema=None,
        response_schema: Schema=None,
    ):
        self.name = name
        self.path = path
        self.methods = methods
        self.func = func
        self.query_parameter_schema = query_parameter_schema
        self.body_schema = body_schema
        self.response_schema = response_schema

    def handler(self):
        if request.accept_mimetypes.best_match([
            "application/json",
            "application/schema+json",
        ]) == "application/schema+json":
            return {}

        params = {}

        try:
            if self.query_parameter_schema:
                params.update(
                    self.query_parameter_schema.validate(
                        request.args
                ))
        except SchemaError as err:
            response = jsonify({"error": str(err)})
            response.status_code = 422
            return response

        try:
            if self.body_schema and request.content_length:
                if request.is_json:
                    params.update(
                        self.body_schema.validate(
                            request.json
                    ))
                else:
                    raise NotImplementedError("Unknown body type, sorry")
        except SchemaError as err:
            response = jsonify({"error": str(err)})
            response.status_code = 422
            return response
                    

        response = self.func(**params)
        if response.is_json and self.response_schema:
            try:
                self.response_schema.validate(response.json)
            except Exception as err:
                warnings.warn(f"Got error when validating the response: {err}")
                
        return response

