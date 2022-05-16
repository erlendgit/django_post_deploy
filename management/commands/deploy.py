from django.core.management.base import BaseCommand
from django.utils import timezone

from post_deploy.models import PostDeployAction
from post_deploy.local_utils import initialize_commands, get_context_manager, get_scheduler_manager


class Command(BaseCommand):
    help = "Execute post deployment actions."

    def __init__(self):
        super(Command, self).__init__()
        self.context_manager = None

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser=parser)
        parser.add_argument('--report', const=True, action='store_const',
                            help="Print the status of all actions.")
        parser.add_argument('--deploy', const=True, action='store_const',
                            help="Execute all pending actions that have auto=True (default setting).")
        parser.add_argument('--execute', help="Execute one of the actions.")

    def handle(self, *args, **options):
        self.context_manager = get_context_manager(None)
        with self.context_manager.execute():
            todo_list = []
            for todo in ['report', 'deploy', 'execute']:
                if options.get(todo):
                    todo_list.append(todo)

            if len(todo_list) != 1:
                self.stderr.write("Provide 1 todo at a time.\n")
                return self.do_help()

            initialize_commands()

            if options['report']:
                return self.do_report()

            if self.has_concurency():
                self.stderr.write("Please wait until all tasks are completed.")
                return

            if options['deploy']:
                return self.do_deploy()

            if options['execute']:
                return self.do_execute([options['execute']])

    def do_help(self):
        self.print_help("manage.py", "post_deploy")

    def has_concurency(self):
        return PostDeployAction.objects.running().exists()

    def do_report(self):

        self.stdout.write("Pending actions that can run automatically:")
        if PostDeployAction.objects.todo().exists():
            for action in PostDeployAction.objects.todo():
                self.stdout.write("* %s" % action.id)
        else:
            self.stdout.write("(no actions)")

        self.stdout.write("\nPending actions that need starting manually:")
        if PostDeployAction.objects.manual().exists():
            for action in PostDeployAction.objects.manual():
                if action.message:
                    self.stdout.write(f"* {action.id} ({action.message})")
                else:
                    self.stdout.write(f"* {action.id}")
        else:
            self.stdout.write("(no actions)")

        self.stdout.write("\nCurrently running actions:")
        if PostDeployAction.objects.running().exists():
            for action in PostDeployAction.objects.running():
                self.stdout.write(f"* {action.id} ({action.started_at})")
        else:
            self.stdout.write("(no actions)")

        self.stdout.write("\nCompleted actions:")
        if PostDeployAction.objects.completed().order_by('-completed_at').exists():
            for action in PostDeployAction.objects.completed().order_by('-completed_at'):
                self.stdout.write(f"* {action.id} ({action.completed_at})")
        else:
            self.stdout.write("(no actions)")

    def do_deploy(self):
        action_ids = []
        for action in PostDeployAction.objects.filter(available=True, auto=True):
            if action.is_auto:
                action_ids.append(action.id)

        self.do_execute(action_ids)

    def do_execute(self, action_ids):
        if action_ids:
            qs = PostDeployAction.objects.filter(id__in=action_ids)
            qs.update(
                started_at=timezone.localtime(),
                completed_at=None,
                message=None,
                done=False
            )

            self.stdout.write("Scheduled execute:")
            for id in action_ids:
                self.stdout.write(f"* {id}")

            task_id = get_scheduler_manager().schedule(action_ids, self.context_manager.default_parameters())
            qs.update(
                task_id=task_id
            )
