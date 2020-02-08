from os import makedirs, path
from typing import Dict, List, Callable
from .schema import (
    Schema,
    QueryParameterSchema,
    UrlParameterSchema,
    SchemaError,
    to_typescript,
)
from flask import Flask, Blueprint, request, jsonify
import warnings
import json

class API:
    def __init__(
            self,
            title: str,
            version: str,
            app: Flask,
            description: str = None,
    ):
        self.app = app
        self.title = title
        self.routes = {}
        self.description = description
        self.version = version

    def add_route(
            self,
            func,
            path,
            name=None,
            methods=None,
            description: str = None,
            url_parameter_schema: UrlParameterSchema=None,
            query_parameter_schema: QueryParameterSchema=None,
            body_schema: Schema=None,
            response_schema: Schema = None,
            blueprint=None,
    ):

        route = Route(
            func=func,
            name=name,
            path=path,
            description=description,
            methods=methods[:],  # make a copy because we might update methods
            url_parameter_schema=url_parameter_schema,
            query_parameter_schema=query_parameter_schema,
            body_schema=body_schema,
            response_schema=response_schema,
        )

        app = self.app
        if blueprint:
            app = blueprint
            # name = f"{blueprint.name}.{name}"

        if "GET" not in [m.upper() for m in methods]:
            methods.append("GET")

        app.add_url_rule(
            path,
            name,
            view_func=route.handle,
            methods=methods,
        )

        self.routes[name] = route

    def route(
        self,
        path,
        name=None,
        methods=None,
        description=None,
        url_parameter_schema: UrlParameterSchema=None,
        query_parameter_schema: QueryParameterSchema=None,
        body_schema: Schema=None,
        response_schema: Dict[int, Schema] = None,
        blueprint: Blueprint = None,
    ):
        def wrapper(func):
            self.add_route(
                func=func,
                name=name,
                path=path,
                methods=methods,
                description=description,
                url_parameter_schema=url_parameter_schema,
                query_parameter_schema=query_parameter_schema,
                body_schema=body_schema,
                response_schema=response_schema,
                blueprint=blueprint,
            )
        return wrapper

    def describe(self):
        return {
            name: route.describe()
            for name, route in self.routes.items()
        }

    def output_ts(self, directory):
        makedirs(directory, exist_ok=True)
        for name, route in self.routes.items():
            f = open(path.join(directory, f"{name}.ts"), "w+")
            f.write(route.describe_ts())
            f.close()

    def output_openapi(self, path, indent=1):
        out = {
            "info": {
                "title": self.title,
                "description": self.description,
                "version": self.version,
            },
            "openapi": "3.0.0.",
            "paths": {},
            # "security": [],
            # "servers": {},
        }

        for name, route in self.routes.items():
            route_path = route.path.replace("<", "{").replace(">", "}")
            out["paths"][route_path] = route.to_openapi()

        f = open(path, "w+")
        f.write(json.dumps(out, indent=indent, sort_keys=True,))
        f.close()



class Route:
    def __init__(
        self,
        name: str,
        path: str,
        methods: str,
        func: Callable,
        response_schema: Schema,
        description: str = None,
        url_parameter_schema: UrlParameterSchema=None,
        query_parameter_schema: QueryParameterSchema=None,
        body_schema: Schema=None,
    ):
        self.name = name
        self.path = path
        self.methods = methods
        self.func = func
        self.description = description
        self.url_parameter_schema = url_parameter_schema
        self.query_parameter_schema = query_parameter_schema
        self.body_schema = body_schema
        self.response_schema = response_schema

    def handle(self, **kwargs):
        if request.accept_mimetypes.best_match([
            "application/json",
            "application/schema+json",
        ]) == "application/schema+json":
            return jsonify(self.to_openapi())

        if request.method == "GET" and "GET" not in self.methods:
            return jsonify(self.to_openapi())

        params = {}

        try:
            if self.url_parameter_schema:
                params.update(
                    self.url_parameter_schema.validate(
                        kwargs
                ))
        except SchemaError as err:
            response = jsonify({"error": str(err)})
            response.status_code = 422
            return response

        try:
            if self.query_parameter_schema:
                params.update(
                    self.query_parameter_schema.validate(
                        request.args.to_dict()
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
        if response.is_json and response.status in self.response_schema:
            try:
                self.response_schema[response.status].validate(response.json)
            except Exception as err:
                warnings.warn(f"Got error when validating the response: {err}")
                
        return response

    def describe_ts(self):
        output = ""
        if self.query_parameter_schema:
            output += to_typescript(
                f"{self.name}_query_schema",
                self.query_parameter_schema,
            ) + "\n"
        
        if self.body_schema:
            output += to_typescript(
                f"{self.name}_body_schema",
                self.body_schema,
            ) + "\n"
        
        for status, response_schema in (self.response_schema or {}).items():
            output += to_typescript(
                f"{self.name}_{status}_response_schema",
                response_schema,
            ) + "\n"

        return output

    def to_openapi(self):
        self.query_parameter_schema.to_openapi() if self.query_parameter_schema else None

        route_data = {
            method.lower(): {
                "operationId": f"{self.name}",
                "description": self.description,
                "parameters": (
                    (self.query_parameter_schema.to_openapi()
                    if self.query_parameter_schema else []) +
                    (self.url_parameter_schema.to_openapi()
                    if self.url_parameter_schema else [])
                ),
                "requestBody": {
                    "content": self.body_schema.to_openapi()
                } if self.body_schema else None,
                "responses": {
                    status_code: {
                        "content": response_schema.to_openapi()
                    } for (status_code, response_schema) in self.response_schema.items()
                },
            } for method in self.methods
        }

        return route_data


    def describe(self):
        return self.describe_ts()
