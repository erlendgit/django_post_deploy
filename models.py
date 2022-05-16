from django.db import models
from django.db.models import Q


class PostDeployActionManager(models.Manager):

    def todo(self):
        return self.get_queryset().filter(auto=True, message__isnull=True, done=False)

    def manual(self):
        return self.get_queryset().filter(Q(auto=False) | Q(done=True, message__isnull=False))

    def completed(self):
        return self.get_queryset().filter(done=True, message__isnull=True)

    def with_errors(self):
        return self.get_queryset().filter(done=True, message__isnull=False)

    def running(self):
        return self.get_queryset().filter(task_id__isnull=False, done=False)


class PostDeployAction(models.Model):
    objects = PostDeployActionManager()

    id = models.CharField(max_length=255, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    auto = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    available = models.BooleanField(default=True)
    done = models.BooleanField(default=False)

    task_id = models.UUIDField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    @property
    def is_auto(self):
        return self.auto and not self.message

    @property
    def status(self):
        if not self.available:
            return 'unavailable'

        if self.is_auto:
            return 'todo'

        if self.message:
            return 'error'

        if self.done:
            return "completed"

        if self.started_at:
            return "started"

        return 'manual'

    @property
    def task_status(self):
        from .tasks import get_status
        if self.task_id:
            result = get_status(self.task_id)
            return result.status
        return ""

    def __str__(self):
        return self.id
