from abc import ABC
from collections import OrderedDict
from inspect import isfunction

from django.utils import timezone

from post_deploy.local_utils import initialize_actions
from post_deploy.models import PostDeployAction


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


def run_deploy_action(action_ids):
    initialize_actions()
    for id in action_ids:
        action = PostDeployAction.objects.get(id=id)
        config = register_post_deploy.class_repository.get(id)

        if config and action:
            try:
                vehicle = config['class']
                if isfunction(vehicle):
                    vehicle()
                else:
                    instance = vehicle()
                    if not isinstance(instance, PostDeployActionBase):
                        raise PostDeployActionBase.InvalidBaseClassError()
                    instance.execute()
            except Exception as e:
                action.message = str(e)
            finally:
                action.completed_at = timezone.localtime()
                action.done = True
                action.save()
