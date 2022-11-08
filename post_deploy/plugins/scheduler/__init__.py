import uuid


class DefaultScheduler():

    def task_ready(self, id):
        return False

    def schedule(self, action_logs, context_kwargs):
        from post_deploy.local_utils import run_deploy_action
        run_deploy_action([l.pk for l in action_logs])
        return uuid.uuid4()
