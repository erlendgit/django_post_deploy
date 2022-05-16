from contextlib import contextmanager
from django_tenants.utils import parse_tenant_config_path, tenant_context

from post_deploy.plugins.context import DefaultContext


class TenantContext(DefaultContext):

    def default_parameters(self):
        return {
            'schema': parse_tenant_config_path()
        }

    @contextmanager
    def execute(self):
        with tenant_context(self.parameters['schema']):
            yield
