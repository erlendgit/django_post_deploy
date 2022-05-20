from celery import Celery
from celery.result import AsyncResult

from django.conf import settings
from django.utils.module_loading import import_string

from post_deploy.errors import PostDeployConfigurationError
from post_deploy.plugins.scheduler import DefaultScheduler


class CeleryScheduler(DefaultScheduler):

    @staticmethod
    def get_celery_app():
        try:
            app = import_string(settings.POST_DEPLOY_CELERY_APP)
            if not isinstance(app, Celery):
                raise PostDeployConfigurationError(
                    f"{settings.POST_DEPLOY_CELERY_APP or 'None'} is not a valid Celery app.")
            return app
        except AttributeError:
            raise PostDeployConfigurationError(
                "Put the path to the celery app in POST_DEPLOY_CELERY at your project settings.")

    def task_ready(self, id):
        app = CeleryScheduler.get_celery_app()
        return AsyncResult(id=id, app=app).ready()

    def schedule(self, action_ids, context_kwargs):
        from post_deploy.tasks import deploy_task
        result = deploy_task.delay(action_ids, context_kwargs)
        return result.id
