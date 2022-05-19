from collections import OrderedDict


class register_post_deploy():
    bindings = OrderedDict()

    def __init__(self, auto=True, description=None):
        self.auto = auto
        self.description = description

    def __call__(self, c):
        app = c.__module__.split('.')[0]
        key = f"{app}.{c.__name__}"
        register_post_deploy.bindings[key] = {
            "class": c,
            "auto": self.auto,
            "description": self.description,
        }
        return c
