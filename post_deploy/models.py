import uuid

from django.db import models
from django.utils import timezone


class PostDeployAction(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    auto = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    available = models.BooleanField(default=True)
    done = models.BooleanField(default=False)

    task_id = models.UUIDField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.id

    def sync_status(self):
        if not self.task_id or self.done:
            return

        from post_deploy.local_utils import get_scheduler_manager
        scheduler = get_scheduler_manager()

        if scheduler.task_ready(str(self.task_id)):
            self.done = True
            self.completed_at = timezone.localtime()
            self.message = "Abnormal termination detected. Please check the logs for details."


class PostDeployLogQuerySet(models.QuerySet):

    def running(self):
        return self.filter(completed_at__isnull=True)

    def import_names(self):
        return [s for s in self.values_list('import_name', flat=True)]

    def completed(self):
        return self.filter(completed_at__isnull=False)

    def with_errors(self):
        return self.filter(has_error=True)

    def unprocessed(self, given):
        all_actions = [key for key in given.keys()]
        processed_actions = {k for k in self.values_list('import_name', flat=True)}
        return [name for name in filter(lambda x: x not in processed_actions, all_actions)]

    def auto(self, given):
        auto_actions = [key for key, config in given.items() if config.get('auto')]
        processed_actions = {k for k in self.values_list('import_name', flat=True)}
        return [name for name in filter(lambda x: x not in processed_actions, auto_actions)]

    def manual(self, given):
        manual_actions = [key for key, config in given.items() if not config.get('auto')]
        processed_actions = {k for k in self.values_list('import_name', flat=True)}
        return [name for name in filter(lambda x: x not in processed_actions, manual_actions)]

    def is_success(self, import_name):
        last_known_run = self.filter(import_name=import_name, completed_at__isnull=False).first()
        if last_known_run:
            return not last_known_run.has_error
        return False

    def is_running(self, import_name):
        return self.running().filter(import_name=import_name).exists()

    def register_action(self, import_name):
        return self.create(import_name=import_name)

    def sync_status(self):
        for action_log in self.running():
            action_log.sync_status()


class PostDeployLog(models.Model):
    class Meta:
        ordering = ("-created_at",)

    objects = PostDeployLogQuerySet.as_manager()

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)

    import_name = models.TextField(null=False)

    created_at = models.DateTimeField(default=timezone.localtime, null=False)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(default=None, null=True)
    task_id = models.UUIDField(blank=True, null=True)

    has_error = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)

    def sync_status(self):
        if not self.task_id or self.completed_at:
            return

        from post_deploy.local_utils import get_scheduler_manager
        scheduler = get_scheduler_manager()

        if scheduler.task_ready(str(self.task_id)):
            self.completed_at = timezone.localtime()
            self.has_error = True
            self.message = "Abnormal termination detected. Please check the logs for details."
            self.save()
