import unittest
from .schema import Schema, Or, Optional, to_typescript

class TestTypescript(unittest.TestCase):
    def test_empty_interface(self):
        s = Schema({})
        result = to_typescript("empty", s)
        expected = \
"""interface empty {
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_basic_types_interface(self):
        s = Schema({
            "some_int": int,
            "some_float": float,
            "some_str": str,
            "some_bool": bool,
        })
        result = to_typescript("empty", s)
        expected = \
"""interface empty {
    some_bool: boolean;
    some_float: number;
    some_int: number;
    some_str: string;
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_or_interface(self):
        s = Schema({
            "some_number_or_str": Or([int, float, str]),

        })
        result = to_typescript("empty", s)
        expected = \
"""interface empty {
    some_number_or_str: number | string;
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_interface_with_list(self):
        s = Schema({
            "list_of_ints":  [int],
        })
        result = to_typescript("moo", s)
        expected = \
"""interface moo {
    list_of_ints: Array<number>;
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_nested_interface(self):
        s = Schema({
            "some_object": {
                "some_int": int
            },
        })
        result = to_typescript("moo", s)
        expected = \
"""interface moo {
    some_object: {
        some_int: number;
    };
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_array_of_nested_interface(self):
        s = Schema({
            "some_object": [{
                "some_int": int
            }],
        })
        result = to_typescript("moo", s)
        expected = \
"""interface moo {
    some_object: Array<{
        some_int: number;
    }>;
}
"""
        self.assertEqual(
            result,
            expected,
        )

    def test_optional_interface(self):
        s = Schema({
            Optional("some_object"): int,
        })
        result = to_typescript("moo", s)
        expected = \
"""interface moo {
    some_object?: number;
}
"""
        self.assertEqual(
            result,
            expected,
        )