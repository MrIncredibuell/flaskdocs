import schema
from schema import *
from itertools import chain

class Schema(schema.Schema):
    def to_typescript(self, name: str = None, description: str = None,):
        return to_typescript(
            name=name or self.name,
            python_schema=self,
            description=description,
        )

    def to_openapi(self):
        raise NotImplementedError

class JsonSchema(Schema):
    def to_openapi(self):
        s = self.json_schema(
            schema_id=None
        )

        del s["$id"]
        del s["$schema"]
    
        return {
            "application/json": {
                "schema": s
            },
        }


def _get_type_name(obj):
    """Return the JSON schema name for a value of a schema object"""
    
    # handle recursive calls where obj is already a type (like from Use)
    if type(obj) == type:
        python_type = obj
    else:
        python_type = type(obj)


    if python_type == str:
        return "string"
    elif python_type == int:
        return "integer"
    elif python_type == float:
        return "number"
    elif python_type == bool:
        return "boolean"
    elif python_type == list:
        raise NotImplementedError("Not ready for non-primitive query params")
        return "array"
    elif python_type == dict:
        raise NotImplementedError("Not ready for non-primitive query params")
        return "object"
    elif python_type == Use:
        try:
            return _get_type_name(obj._callable)
        except Exception as e:
            pass
    return "string"


class QueryParameterSchema(Schema):
    def to_openapi(self):
        params = []
        for name, value in self._schema.items():
            try:
                description = name.description
            except:
                description = ""
            params.append({
                "name": str(name),
                "in": "query",
                "required": not isinstance(name, Optional),
                "schema": {
                    "type": _get_type_name(value)
                },
                "description": description,
            })
        return params

class UrlParameterSchema(QueryParameterSchema):
    def to_openapi(self):
        params = []
        for name, value in self._schema.items():
            try:
                description = name.description
            except:
                description = ""
            params.append({
                "name": str(name),
                "in": "path",
                "required": not isinstance(name, Optional),
                "schema": {
                    "type": _get_type_name(value)
                },
                "description": description,
            })
        return params
    


INDENT_WIDTH = 4

def _typescript_predicate(value, indent=0):
    # return an object
    if type(value) in (dict, Schema):
        if type(value) == dict:
            value = Schema(value)
        return [_to_interface(
            value,
            indent=indent,
        )]

    # return an array
    if type(value) in (list,):
        array_type = " | ".join(_typescript_predicate(
            Or(value),
            indent=indent,
        ))
        return [f"Array<{array_type}>"]

    # return a list of types
    if type(value) in (And, Or):
        x = list(chain(
            *(_typescript_predicate(v, indent=indent) for v in value._args)
        ))
        return x

    # return a basic type
    if type(value) == type:
        return [{
            int: "number",
            float: "number",
            str: "string",
            bool: "boolean",
        }.get(value, "any")]
    
    return []

def _to_interface(python_schema: Schema, indent=0):
    output = "{\n"

    #indent the nested key-values
    temp_indent = indent + INDENT_WIDTH

    # TODO: Think about making this order strict
    for k, v in python_schema._schema.items():
        optional = type(k) == Optional
        if optional:
            k = k.schema # extract the key

        typescript_types = " | ".join(sorted(set(_typescript_predicate(v, indent=temp_indent))))

        # never have a blank type
        if typescript_types == "":
            typescript_types = "any"

        output += f"{' ' * temp_indent}{k}{'?' if optional else ''}: {typescript_types};\n"

    return output + (" " * indent) + "}"


def to_typescript(name: str, python_schema: Schema, description: str = None):
    
    # TODO: validate name is typescript safe

    output = f"interface {name} " + _to_interface(
        python_schema=python_schema,
        indent=0,
    )
    return output + "\n"