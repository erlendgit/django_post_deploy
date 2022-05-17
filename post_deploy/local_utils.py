from django.conf import settings
from django.utils.module_loading import import_string

from post_deploy.models import PostDeployAction
from post_deploy.plugins.context import DefaultContext
from post_deploy.plugins.scheduler import DefaultScheduler


def initialize_commands():
    from post_deploy.utils import register_post_deploy
    action_list = {}

    for app in settings.INSTALLED_APPS:
        try:
            __import__(f"{app}.post_deploy")
        except ModuleNotFoundError:
            pass

    for id, configuration in register_post_deploy.class_repository.items():
        action, created = PostDeployAction.objects.get_or_create(id=id)
        action.auto = configuration['auto']
        action.description = configuration['description']
        action.save()

        action_list[id] = action

    current_actions = action_list.keys()
    for action in PostDeployAction.objects.filter(available=True):
        if action.id not in current_actions:
            action.available = False
            action.save()

    return action_list


def get_context_manager(context_parameters) -> DefaultContext:
    Manager = import_string(getattr(settings, 'POST_DEPLOY_CONTEXT_MANAGER', 'post_deploy.plugins.context.DefaultContext'))
    return Manager(context_parameters)


def get_scheduler_manager() -> DefaultScheduler:
    Manager = import_string(getattr(settings, 'POST_DEPLOY_SCHEDULER_MANAGER', 'post_deploy.plugins.scheduler.DefaultScheduler'))
    return Manager()
