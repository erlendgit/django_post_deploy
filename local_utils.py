from celery import Celery
from django.conf import settings

from post_deploy.errors import PostDeployConfigurationError
from post_deploy.models import PostDeployAction
from post_deploy.utils import register_post_deploy


def get_celery_app():
    try:
        app = __import__(settings.POST_DEPLOY_CELERY_APP).celery_app
        if not isinstance(app, Celery):
            raise PostDeployConfigurationError(f"{settings.POST_DEPLOY_CELERY_APP} is not a valid Celery app.")
        return app
    except AttributeError:
        raise PostDeployConfigurationError("Put the module where 'celery_app' can be found in POST_DEPLOY_CELERY at your project settings.")


def initialize_commands():
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
