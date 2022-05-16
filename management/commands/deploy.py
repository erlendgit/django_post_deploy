from django.core.management.base import BaseCommand
from django.utils import timezone

from core.lib import tenant_schema
from post_deploy.models import PostDeployAction
from post_deploy.local_utils import initialize_commands


class Command(BaseCommand):
    help = "Execute post deployment actions."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser=parser)
        parser.add_argument('--report', const=True, action='store_const',
                            help="Print the status of all actions.")
        parser.add_argument('--execute', const=True, action='store_const',
                            help="Execute all pending actions that have auto=True (default setting).")
        parser.add_argument('--execute-one', help="Execute one of the actions.")

    def handle(self, *args, **options):
        if tenant_schema() == 'public':
            return

        todo_list = []
        for todo in ['report', 'execute', 'execute-one']:
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

        if options['execute']:
            return self.do_deploy()

        if options['execute-one']:
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
        from post_deploy.tasks import execute_task

        if action_ids:
            task = execute_task.delay(tenant_schema(), action_ids)

            PostDeployAction.objects.filter(id__in=action_ids).update(
                started_at=timezone.localtime(),
                completed_at=None,
                message=None,
                done=False,
                task_id=task.id,
            )

            self.stdout.write("Scheduled execute:")
            for id in action_ids:
                self.stdout.write(f"* {id}")
