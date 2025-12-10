from post_deploy.local_utils import get_context_manager, run_deploy_action
from post_deploy.plugins.scheduler.celery import CeleryScheduler

app = CeleryScheduler.get_celery_app()


@app.task(bind=True)
def deploy_task(self, log_record_pks, context_parameters):
    try:
        manager = get_context_manager(context_parameters)
        with manager.execute():
            run_deploy_action(log_record_pks)
    except ModuleNotFoundError:
        self.retry(countdown=300, max_retries=6)
