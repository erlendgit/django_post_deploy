Django Post Deploy
===

This module adds a way automate release-specific post-deploy/post-migrate actions to your Django project.

### Features

* Allow actions to be scheduled with the deployment automation
  * But also give the oppurtunity to keep special actions out of the automation and have those executed manually.
* Schedule the actions to be executed in Celery.
  * The task scheduler is configurable, so you can write your own.
* Support for django_tenants.

### Alternatives

Alternative to this module you can use:

* Management tasks. Used once and in the future confuse developers "Must we also maintain this code?"
* "Empty" migrations. That
  * may or may not activate all custom expected code for it...
  * may or may not depend on other migrations being completed.

### Why use this module?

This module is of use for your application if you:

* want to keep management commands clean of one-time-used code.
* want to have release finishing tasks executed in a certain and known state of the application.

## Example

```python
# Inside a custom django module's post_deploy.py
from post_deploy import post_deploy_action

@post_deploy_action
def make_non_code_changes_to_complete_the_next_release():
    pass

@post_deploy_action(auto=False)
def this_action_must_be_triggered_manually():
    pass
```

```shell
# This line is added to your deployment automation script
python manage.py deploy --auto
```

```shell
# This line is executed when the time is right for specific actions
$ ./manage.py deploy --one core.this_action_must_be_triggered_manually

# Or like this: both auto and manual actions are scheduled:
$ ./manage.py deploy --all

# Inspect the status of the actions like so, to see if there are errors for any action.
$ ./manage.py deploy --report
```

## Configuration

Out of the box the deploy management command runs the actions serially. However, if you use Celery you have to add this to your settings:

### Celery

```python
# inside your projects settings.py file:

POST_DEPLOY_CELERY_APP = 'module.path.to.your.projects.celery.app'
POST_DEPLOY_SCHEDULER_MANAGER = 'post_deploy.plugins.scheduler.celery.CeleryScheduler'
```

### Custom scheduler manager

Below is a partial copy of othe Celery scheduler manager as an example on how to write one for your alternative task scheduler:

**NOTICE: remember to configure your custom scheduler manager in your project settings.**

```python
from celery import Celery
from celery.result import AsyncResult

from post_deploy.plugins.scheduler import DefaultScheduler


class CeleryScheduler(DefaultScheduler):
    ...

    def task_ready(self, id):
        return AsyncResult(id=id, app=...).ready()

    def schedule(self, action_ids, context_kwargs):
        from post_deploy.tasks import deploy_task
        result = deploy_task.delay(action_ids, context_kwargs)
        return result.id

    ...
```

### Django tenants

This module supports the django_tenants module. In order to make the post deploy actions tenant aware two things are different from normal operation. You have to (1) configure a context manager, and (2) the management command is a little different.

```python
# inside your projects settings.py file:

POST_DEPLOY_CONTEXT_MANAGER = 'post_deploy.plugins.context.tenant.TenantContext'
```

```shell
# The tenant schema is transported to the celery task runner when the management
# command is executed in the given schema aware management commands. For example:

# all_tenants_command example:
$ ./manage.py all_tenants_command deploy --all

# tenant_command example:
$ ./manage.py tenant_command deploy --report --schema=public
```

Example on how to have actions behave different based on the selected schema:

```python
# Inside a module's post_deploy.py
from django_tenants.utils import parse_tenant_config_path
from post_deploy import post_deploy_action

@post_deploy_action
def example_on_how_alter_operation_based_on_schema():
    if parse_tenant_config_path("") == 'public':
        # Do 'public' specific operations.
        pass
  
    # else, proceed as required.
    ...
```

## Technical details

* This module provides a model, and therefore require a common relational database to be installed. There are however no relations between multiple models in this module, so it may be possible that it works with a non-relational database too. But it is not tested in non-relational database configurations.

## License information

django_post_deploy (c) by Erlend ter Maat

django_post_deploy is licensed under a
Creative Commons Attribution-ShareAlike 4.0 International License.

You should have received a copy of the license along with this
work. If not, see <http://creativecommons.org/licenses/by-sa/4.0/>.
