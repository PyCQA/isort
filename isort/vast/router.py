"""Defines how to store the routes that direct text-content to specific
handlers that form the VERY Abstract Syntax Tree.
"""

class Router(object):
    """Routes specific text patterns to handlers that define how the content will be transformed
    creating a VERY Abstract Syntax Tree.
    """
    __slots__ = ('routes', )

    def __init__(self, *routes):
        self.routes = OrderedDict()
        for route in routes:
            self.add(*route[1:])(route[0])

    def add(self, *match):
        def decorator(handler):
            if isinstance(handler.start_on, str):
                handler.start_on = (handler.start_on, )
            if isinstance(handler.end_on, str):
                handler.end_on = (handler.end_on, )
            for match_on in (match + handler.start_on):
                self.routes[match_on] = handler
            return handler
        return decorator

    @property
    def match_on(self):
        return tuple(self.routes.keys())


    def __getitem__(self, item):
        return self.routes[item]

    def get(self, *args):
        return self.routes.get(*args)

    def excluding(self, *routes):
        new_router = deepcopy(self)
        for route in routes:
            del new_router.routes[route]

        return new_router
