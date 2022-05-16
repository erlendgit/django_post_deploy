import uuid


class DefaultScheduler():

    def task_status(self, id):
        return 'PENDING'

    def schedule(self, action_ids, context_kwargs):
        from post_deploy.utils import run_deploy_action
        run_deploy_action(action_ids)
        return uuid.uuid4()
