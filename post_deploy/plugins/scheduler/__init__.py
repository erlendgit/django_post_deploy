import uuid


class DefaultScheduler():

    def task_ready(self, id):
        return False

    def schedule(self, action_ids, context_kwargs):
        from post_deploy.local_utils import run_deploy_action
        run_deploy_action(action_ids)
        return uuid.uuid4()
