from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.timezone import get_current_timezone as ltz

from post_deploy.local_utils import initialize_actions, get_context_manager, get_scheduler_manager, model_ok

from post_deploy.models import PostDeployLog


class Command(BaseCommand):
    help = "Execute post deployment actions."
    _bindings = None

    def __init__(self):
        super(Command, self).__init__()
        self.context_manager = None

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser=parser)
        parser.add_argument('--status', const=True, action='store_const',
                            help="Print the status of all previous actions.")
        parser.add_argument('--todo', const=True, action='store_const',
                            help="Print the status of posible future actions.")
        parser.add_argument('--auto', const=True, action='store_const',
                            help="Execute all pending actions that have auto=True (default setting).")
        parser.add_argument('--all', const=True, action='store_const',
                            help="Execute all pending actions no matter the value of auto.")
        parser.add_argument('--one', help="Execute one of the actions.")
        parser.add_argument('--once', help="Execute the given action if it is not completed correctly.")
        parser.add_argument('--skip', const=True, action='store_const', help="Skip all unprocessed tasks.")

    def handle(self, *args, **options):
        self.context_manager = get_context_manager(None)
        with self.context_manager.execute():
            if not model_ok('post_deploy.PostDeployLog'):
                self.stdout.write("Model is not ready. Is your site configured properly?")
                return

            self._bindings = initialize_actions()
            PostDeployLog.objects.sync_status()

            todo_list = []
            for todo in ['status', 'todo', 'auto', 'all', 'one', 'once', 'skip']:
                if options.get(todo):
                    todo_list.append(todo)

            if len(todo_list) != 1:
                self.stderr.write("Provide 1 todo at a time.\n")
                return self.do_help()

            if 'status' in todo_list:
                return self.do_status()

            if 'todo' in todo_list:
                return self.do_todo()

            if 'skip' in todo_list:
                return self.do_skip()

            if 'auto' in todo_list:
                return self.do_execute(PostDeployLog.objects.auto(self._bindings))

            if 'all' in todo_list:
                return self.do_execute(PostDeployLog.objects.unprocessed(self._bindings))

            if 'once' in todo_list:
                return self.do_once(options['once'])

            if 'one' in todo_list:
                return self.do_one(options['one'])

    def do_help(self):
        self.print_help("manage.py", "post_deploy")

    def do_skip(self):
        for import_name in PostDeployLog.objects.unprocessed(self._bindings):
            action_log:PostDeployLog = PostDeployLog.objects.register_action(import_name)
            action_log.started_at = timezone.localtime()
            action_log.completed_at = timezone.localtime()
            action_log.save()

    def do_once(self, import_name):
        if not PostDeployLog.objects.is_success(import_name):
            self.do_execute([import_name])
        else:
            self.stdout.write("Already completed %s" % import_name)

    def do_one(self, import_name):
        return self.do_execute([import_name])

    def do_status(self):
        if PostDeployLog.objects.running().exists():
            self.stdout.write("\nCurrently running actions:")
            for action in PostDeployLog.objects.running():
                start = action.started_at or action.created_at
                self.stdout.write(f"* {action.import_name} ({start.astimezone(ltz())})")

        if PostDeployLog.objects.completed().with_errors().exists():
            self.stdout.write("\nActions that failed:")
            for action in PostDeployLog.objects.with_errors():
                self.stdout.write(f"* {action.import_name} ({action.completed_at.astimezone(ltz())} {action.message})")

        if PostDeployLog.objects.completed().order_by('-completed_at').exists():
            self.stdout.write("\nCompleted actions:")
            for action in PostDeployLog.objects.completed().order_by('-completed_at'):
                self.stdout.write(f"* {action.import_name} ({action.completed_at.astimezone(ltz())})")

    def do_todo(self):
        auto_actions = PostDeployLog.objects.auto(self._bindings)
        if auto_actions:
            for import_name in auto_actions:
                self.stdout.write("a: %s" % import_name)

        manual_actions = PostDeployLog.objects.manual(self._bindings)
        if manual_actions:
            for import_name in manual_actions:
                self.stdout.write(f"m: {import_name}")

        if PostDeployLog.objects.completed().with_errors().exists():
            for action in PostDeployLog.objects.completed().with_errors():
                self.stdout.write(f"F: {action.import_name} ({action.message})")

    def do_execute(self, import_names):
        actions = []
        for name in import_names:
            if PostDeployLog.objects.is_running(name):
                self.stdout.write("Still running %s" % name)
            else:
                actions.append(name)

        if len(actions) == 0:
            self.stdout.write(f"No actions scheduled.")
            return

        action_logs = []
        for import_name in actions:
            PostDeployLog.objects.filter(import_name=import_name).delete()
            action_logs.append(PostDeployLog.objects.register_action(import_name))
            self.stdout.write(f"Scheduled {import_name}")

        task_id = get_scheduler_manager().schedule(action_logs, self.context_manager.default_parameters())
        PostDeployLog.objects.filter(import_name__in=actions).update(
            task_id=task_id
        )
