from post_deploy.local_utils import get_context_manager, run_deploy_action
from post_deploy.plugins.scheduler.celery import CeleryScheduler

app = CeleryScheduler.get_celery_app()


@app.task
def deploy_task(log_record_pks, context_parameters):
    manager = get_context_manager(context_parameters)
    with manager.execute():
        run_deploy_action(log_record_pks)
