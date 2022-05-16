from abc import ABC
from collections import OrderedDict


class register_post_deploy():
    class_repository = OrderedDict()

    def __init__(self, auto=True, description=None):
        self.auto = auto
        self.description = description

    def __call__(self, c):
        app = c.__module__.split('.')[0]
        key = f"{app}.{c.__name__}"
        register_post_deploy.class_repository[key] = {
            "class": c,
            "auto": self.auto,
            "description": self.description,
        }
        return c


class PostDeployActionBase(ABC):
    class InvalidBaseClassError(Exception):
        pass

    def execute(self):
        raise NotImplementedError()

    def revert(self):
        pass
