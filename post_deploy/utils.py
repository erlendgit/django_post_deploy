from collections import OrderedDict
from functools import partial, update_wrapper
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
        key = f"{c.__module__}.{c.__qualname__}"
        register_post_deploy.bindings[key] = {
            "auto": self.auto,
            "description": self.description,
        }


def skip_all_tasks(reason):
    from post_deploy.local_utils import initialize_actions
    from post_deploy.models import PostDeployLog

    actions = initialize_actions()
    for import_name in actions.keys():
        PostDeployLog.objects.skip_action(import_name, reason)


def run_task(import_name):
    from django.utils.translation import gettext as _
    from post_deploy.local_utils import get_context_manager, get_scheduler_manager
    from post_deploy.models import PostDeployLog
    assert not PostDeployLog.objects.is_running(import_name), _("Task is already running")

    context_manager = get_context_manager(None)
    action_log = PostDeployLog.objects.register_action(import_name)
    task_id = get_scheduler_manager().schedule([action_log], context_manager.default_parameters())
    PostDeployLog.objects.filter(import_name=import_name).update(task_id=task_id)
