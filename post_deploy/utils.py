from collections import OrderedDict
from functools import update_wrapper, partial
from inspect import isfunction


class register_post_deploy():
    bindings = OrderedDict()

    decorated = None

    def __init__(self, *args, **kwargs):
        # Copy configuration. Provide defaults if kwargs is empty.
        self.auto = kwargs.get('auto', True)
        self.description = kwargs.get('description', "")

        if self.args_has_one_function(args):
            # Decorated without configuration.
            self.register_input(*args)
            self.decorated = args[0]
            update_wrapper(self, self.decorated)

    def args_has_one_function(self, args):
        if len(args) == 0:
            return False
        if len(args) > 1 or not isfunction(args[0]):
            raise ValueError("Specify keyword arguments when using this decorator.")
        return True

    def __get__(self, obj):
        return partial(self, obj)

    def __call__(self, *args, **kwargs):
        if not self.decorated:
            # Decorated with configuration.
            self.register_input(*args)
            return args[0]

        return self.decorated(*args, **kwargs)

    def register_input(self, c):
        app = c.__module__.split('.')[0]
        key = f"{app}.{c.__name__}"
        register_post_deploy.bindings[key] = {
            "class": c,
            "auto": self.auto,
            "description": self.description,
        }
