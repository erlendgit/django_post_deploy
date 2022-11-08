from unittest import mock

from django.test.testcases import TestCase
from django.utils import timezone

from post_deploy.models import PostDeployLog


class TestLogQueryset(TestCase):
    def setUp(self):
        self.error_action_record = PostDeployLog.objects.create(
            import_name='some.completed_with_error_action',
            started_at=timezone.localtime(),
            completed_at=timezone.localtime(),
            has_error=True,
            message="Error message"
        )
        self.another_error_record = PostDeployLog.objects.create(
            import_name='some.another_completed_with_error_action',
            started_at=timezone.localtime(),
            completed_at=timezone.localtime(),
            has_error=True,
            message="Error message"
        )
        self.fine_action_record = PostDeployLog.objects.create(
            import_name='some.completed_fine_action',
            started_at=timezone.localtime(),
            completed_at=timezone.localtime(),
        )
        self.running_action_record = PostDeployLog.objects.create(
            import_name='some.running_action'
        )
        self.reference = {
            "some.completed_fine_action": {},
            "some.other_action": {},
            "some.other_auto_action": {'auto': True}
        }

    def test_running(self):
        self.assertEqual(PostDeployLog.objects.count(), 4)
        self.assertEqual(PostDeployLog.objects.running().count(), 1)
        self.assertEqual(PostDeployLog.objects.running().first().import_name, 'some.running_action')

    def test_import_names(self):
        self.assertEqual(PostDeployLog.objects.count(), 4)
        self.assertEqual(PostDeployLog.objects.import_names(), [
            'some.running_action',
            'some.completed_fine_action',
            'some.another_completed_with_error_action',
            'some.completed_with_error_action',
        ])

    def test_completed(self):
        self.assertEqual(PostDeployLog.objects.completed().count(), 3)
        self.assertEqual(PostDeployLog.objects.completed().import_names(), [
            'some.completed_fine_action',
            'some.another_completed_with_error_action',
            'some.completed_with_error_action',
        ])

    def test_with_errors(self):
        self.assertEqual(PostDeployLog.objects.with_errors().count(), 2)
        self.assertEqual(PostDeployLog.objects.with_errors().import_names(), [
            'some.another_completed_with_error_action',
            'some.completed_with_error_action',
        ])

    def test_unprocessed(self):
        self.assertEqual(PostDeployLog.objects.unprocessed(self.reference), [
            'some.other_action',
            'some.other_auto_action',
        ])

    def test_auto(self):
        self.assertEqual(PostDeployLog.objects.auto(self.reference), [
            'some.other_auto_action',
        ])

    def test_manual(self):
        self.assertEqual(PostDeployLog.objects.manual(self.reference), [
            'some.other_action',
        ])

    def test_is_success(self):
        self.assertEqual(PostDeployLog.objects.is_success('some.completed_fine_action'), True)
        self.assertEqual(PostDeployLog.objects.is_success('some.completed_with_error_action'), False)
        self.assertEqual(PostDeployLog.objects.is_success('some.unprocessed_item'), False)

    def test_is_running(self):
        self.assertEqual(PostDeployLog.objects.is_running('some.running_action'), True)
        self.assertEqual(PostDeployLog.objects.is_running('some.completed_fine_action'), False)
        self.assertEqual(PostDeployLog.objects.is_running('some.completed_with_error_action'), False)
        self.assertEqual(PostDeployLog.objects.is_running('some.unprocessed_item'), False)

    def test_register_action(self):
        record: PostDeployLog = PostDeployLog.objects.register_action('some.completed_with_error_action')
        self.error_action_record.refresh_from_db()

        # a new record is created
        self.assertEqual(record.import_name, self.error_action_record.import_name)
        self.assertNotEqual(record.pk, self.error_action_record.pk)

    @mock.patch('post_deploy.models.PostDeployLog.sync_status')
    def test_sync_status(self, sync_status):
        PostDeployLog.objects.sync_status()
        self.assertEqual(sync_status.call_count, 1)
