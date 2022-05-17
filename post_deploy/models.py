from django.db import models


class PostDeployActionQueryset(models.QuerySet):

    def available(self):
        return self.filter(available=True)

    def unprocessed(self):
        return self.available().filter(started_at__isnull=True)

    def todo(self):
        return self.unprocessed().filter(auto=True)

    def manual(self):
        return self.unprocessed().filter(auto=False)

    def completed(self):
        return self.filter(done=True, message__isnull=True)

    def with_errors(self):
        return self.filter(message__isnull=False)

    def running(self):
        return self.filter(started_at__isnull=False, done=False)

    def ids(self):
        return self.values_list('id', flat=True)


class PostDeployAction(models.Model):
    objects = PostDeployActionQueryset.as_manager()

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

    def __str__(self):
        return self.id
