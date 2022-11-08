import uuid
from unittest import mock

from django.test.testcases import TestCase
from django.utils import timezone

from post_deploy.models import PostDeployLog

from post_deploy.plugins.scheduler import DefaultScheduler

from django_post_deploy.post_deploy.local_utils import get_context_manager


class TestManagementCommandTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.initialize_actions = mock.patch("post_deploy.management.commands.deploy.initialize_actions").start()
        self.initialize_actions.return_value = {
            'some.auto_action': {
                'auto': True,
                'description': 'description',
            },
            'some.manual_action': {
                'auto': False,
                'description': None
            },
            'some.completed_with_error_action': {
                'auto': True,
                'description': None
            },
            'some.completed_fine_action': {
                'auto': True,
                'description': None,
            },
            'some.still_running_action': {
                'auto': True,
                'description': None,
            }
        }
        PostDeployLog.objects.create(
            import_name='some.completed_with_error_action',
            started_at=timezone.localtime(),
            completed_at=timezone.localtime(),
            has_error=True,
            message="Error message"
        )
        PostDeployLog.objects.create(
            import_name='some.completed_fine_action',
            started_at=timezone.localtime(),
            completed_at=timezone.localtime(),
        )
        PostDeployLog.objects.create(
            import_name='some.still_running_action',
            started_at=timezone.localtime(),
        )
        PostDeployLog.objects.create(
            import_name='custom_still_running_action',
            started_at=timezone.localtime(),
        )

        from post_deploy.management.commands.deploy import Command as DeployCommand
        self.command = DeployCommand()
        self.command.stdout = mock.MagicMock()
        self.command.stderr = mock.MagicMock()

    def tearDown(self):
        mock.patch.stopall()
        super().tearDown()

    @mock.patch('post_deploy.management.commands.deploy.Command.do_status')
    def test_status(self, do_status):
        self.command.handle(status=True)
        self.assertEqual(do_status.call_count, 1)

    @mock.patch('post_deploy.management.commands.deploy.Command.do_todo')
    def test_todo(self, do_todo):
        self.command.handle(todo=True)
        self.assertEqual(do_todo.call_count, 1)

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_auto(self, do_execute):
        self.command.handle(auto=True)
        self.assertEqual(do_execute.call_args.args, (["some.auto_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_all(self, do_execute):
        self.command.handle(all=True)
        self.assertEqual(do_execute.call_args.args, (["some.auto_action", 'some.manual_action'],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_one(self, do_execute):
        self.command.handle(one="some.auto_action")
        self.assertEqual(do_execute.call_args.args, (["some.auto_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_one_completed(self, do_execute):
        self.command.handle(one="some.completed_fine_action")
        self.assertEqual(do_execute.call_args.args, (["some.completed_fine_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_one_custom(self, do_execute):
        self.command.handle(one="custom_action")
        self.assertEqual(do_execute.call_args.args, (["custom_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_once(self, do_execute):
        self.command.handle(once="some.auto_action")
        self.assertEqual(do_execute.call_args.args, (["some.auto_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_once_custom_action(self, do_execute):
        self.command.handle(once="custom_action")
        self.assertEqual(do_execute.call_args.args, (["custom_action"],))

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_once_on_completed_action(self, do_execute):
        self.command.handle(once="some.completed_fine_action")
        self.assertEqual(do_execute.call_count, 0)

    @mock.patch('post_deploy.management.commands.deploy.Command.do_execute')
    def test_once_on_failed_action(self, do_execute):
        self.command.handle(once="some.completed_with_error_action")
        self.assertEqual(do_execute.call_args.args, (["some.completed_with_error_action"],))

    def test_skip(self):
        self.command.handle(skip=True)

        completed_actions = PostDeployLog.objects.completed().import_names()
        self.assertIn('some.auto_action', completed_actions)
        self.assertIn('some.manual_action', completed_actions)
        self.assertNotIn('custom_action', completed_actions)

    @mock.patch('post_deploy.management.commands.deploy.get_scheduler_manager')
    def test_do_execute(self, get_scheduler_manager):
        scheduler_manager = mock.MagicMock(spec=DefaultScheduler)
        scheduler_manager.schedule.return_value = uuid.uuid4()
        get_scheduler_manager.return_value = scheduler_manager

        self.command.context_manager = get_context_manager(None)
        self.command.do_execute([
            'some.auto_action',
            'some.manual_action',
            'some.completed_with_error_action',
            'some.completed_fine_action',
            'some.still_running_action',
            'custom_still_running_action',
        ])

        # ensure only non-running tasks are scheduled
        scheduled_tasks = [r.import_name for r in scheduler_manager.schedule.call_args.args[0]]
        self.assertEqual(scheduled_tasks, [
            'some.auto_action',
            'some.manual_action',
            'some.completed_with_error_action',
            'some.completed_fine_action',
        ])

        # ensure only one record an action exists.
        for task in [
            'some.auto_action',
            'some.manual_action',
            'some.completed_with_error_action',
            'some.completed_fine_action']:
            self.assertEqual(PostDeployLog.objects.filter(import_name=task).count(), 1, msg="Found more then 1 record for %s" % task)
