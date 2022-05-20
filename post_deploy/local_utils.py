from inspect import isfunction

from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from post_deploy.models import PostDeployAction
from post_deploy.plugins.context import DefaultContext
from post_deploy.plugins.scheduler import DefaultScheduler
from post_deploy.utils import register_post_deploy


def initialize_actions():
    from post_deploy.utils import register_post_deploy
    action_list = {}

    for app in settings.INSTALLED_APPS:
        try:
            __import__(f"{app}.post_deploy")
        except ModuleNotFoundError:
            pass

    for id, configuration in register_post_deploy.bindings.items():
        action, created = PostDeployAction.objects.get_or_create(id=id)
        action.auto = configuration['auto']
        action.description = configuration['description']
        action.sync_status()
        action.save()

        action_list[id] = action

    current_actions = action_list.keys()
    for action in PostDeployAction.objects.filter(available=True):
        if action.id not in current_actions:
            action.available = False
            action.save()

    return action_list


def run_deploy_action(action_uuids):
    initialize_actions()
    for uuid in action_uuids:
        action = PostDeployAction.objects.get(uuid=uuid)
        config = register_post_deploy.bindings.get(action.id)

        if config and action:
            try:
                vehicle = config['class']
                if isfunction(vehicle):
                    vehicle()
                else:
                    raise Exception(f"{vehicle} is not a function")
            except Exception as e:
                action.message = str(e)
            finally:
                action.completed_at = timezone.localtime()
                action.done = True
                action.save()


def get_context_manager(context_parameters) -> DefaultContext:
    Manager = import_string(
        getattr(settings, 'POST_DEPLOY_CONTEXT_MANAGER', 'post_deploy.plugins.context.DefaultContext'))
    return Manager(context_parameters)


def get_scheduler_manager() -> DefaultScheduler:
    Manager = import_string(
        getattr(settings, 'POST_DEPLOY_SCHEDULER_MANAGER', 'post_deploy.plugins.scheduler.DefaultScheduler'))
    return Manager()
