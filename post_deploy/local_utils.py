import logging
from inspect import isfunction

import django.db
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from django.utils.module_loading import import_string

from post_deploy.models import PostDeployLog
from post_deploy.plugins.context import DefaultContext
from post_deploy.plugins.scheduler import DefaultScheduler

logger = logging.getLogger(__name__)


def initialize_actions():
    for app in apps.get_app_configs():
        try:
            __import__(f"{app.module.__name__}.post_deploy")
        except ModuleNotFoundError:
            pass

    from post_deploy.utils import register_post_deploy
    return register_post_deploy.bindings


def run_deploy_action(action_log_pks):
    for pk in action_log_pks:
        action_log = PostDeployLog.objects.get(pk=pk)
        action_log.started_at = timezone.localtime()
        action_log.save()
        try:
            vehicle = import_string(action_log.import_name)
            vehicle()
        except Exception as e:
            action_log.message = str(e)
            action_log.has_error = True
        finally:
            action_log.completed_at = timezone.localtime()
            action_log.save()


def get_context_manager(context_parameters) -> DefaultContext:
    Manager = import_string(
        getattr(settings, 'POST_DEPLOY_CONTEXT_MANAGER', 'post_deploy.plugins.context.DefaultContext'))
    return Manager(context_parameters)


def get_scheduler_manager() -> DefaultScheduler:
    Manager = import_string(
        getattr(settings, 'POST_DEPLOY_SCHEDULER_MANAGER', 'post_deploy.plugins.scheduler.DefaultScheduler'))
    return Manager()


def model_ok(model_name):
    try:
        Model = apps.get_model(model_name)
        Model.objects.count()
        return True
    except django.db.ProgrammingError as e:
        logger.warning(e)
    return False
