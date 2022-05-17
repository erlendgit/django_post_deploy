from post_deploy.local_utils import get_context_manager
from post_deploy.plugins.scheduler.celery import CeleryScheduler
from post_deploy.utils import run_deploy_action

app = CeleryScheduler.get_celery_app()


@app.task
def deploy_task(task_ids, context_parameters):
    manager = get_context_manager(context_parameters)
    with manager.execute():
        run_deploy_action(task_ids)
