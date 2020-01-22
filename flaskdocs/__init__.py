from typing import List

class API:
    def __init__(
            self,
            name: str,
            description: str = None,
    ):
        self.name = name
        self.routes = {}

    def add_route(
            self,
            path,
            name=None,
            methods=None,
    ):

        self.routes[name] = Route(
            name=name,
            path=path,
            methods=methods or [],
        )

        return

    def describe(self):
        return ""

class Route:
    def __init__(
        self,
        name: str,
        path: str,
        methods: List,
    ):
        self.name = name
        self.path = path
        self.methods = []

