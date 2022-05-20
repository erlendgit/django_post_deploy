from contextlib import contextmanager
from django_tenants.utils import parse_tenant_config_path, schema_context

from post_deploy.plugins.context import DefaultContext


class TenantContext(DefaultContext):

    def default_parameters(self):
        return {
            'schema': parse_tenant_config_path("")
        }

    @contextmanager
    def execute(self):
        with schema_context(self.parameters['schema']):
            yield
