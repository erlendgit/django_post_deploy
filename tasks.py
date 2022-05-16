from inspect import isfunction

from celery.result import AsyncResult
from django.utils import timezone
from django_tenants.utils import schema_context

from post_deploy.local_utils import get_celery_app, initialize_commands
from post_deploy.models import PostDeployAction
from post_deploy.utils import register_post_deploy, PostDeployActionBase

app = get_celery_app()


@app.task
def execute_task(schema, task_ids):
    with schema_context(schema):
        initialize_commands()
        for task_id in task_ids:
            action = PostDeployAction.objects.get(id=task_id)
            config = register_post_deploy.class_repository.get(task_id)
            run_deploy_action(action, config)

    return True


def run_deploy_action(action, config):
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


def get_status(id):
    return AsyncResult(str(id), app=app)
