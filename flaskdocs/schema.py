from schema import *
from itertools import chain

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
            *(_typescript_predicate(v, indent=indent) for v in value._args[0])
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

    for k, v in sorted(python_schema._schema.items()):
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