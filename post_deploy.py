import warnings
from time import sleep

from post_deploy.utils import register_post_deploy, PostDeployActionBase


@register_post_deploy()
class SomeDeployAction(PostDeployActionBase):
    def execute(self):
        warnings.warn("START SOMEDEPLOYACTION")
        sleep(60)
        warnings.warn("END SOMEDEPLOYACTION")


@register_post_deploy(auto=False, description="Wait until all of this feature is ready.")
class PutMoreEffortSomeDeployAction(PostDeployActionBase):
    def execute(self):
        warnings.warn("START SOMEDEPLOYACTION")
        sleep(60)
        warnings.warn("END SOMEDEPLOYACTION")


@register_post_deploy(description="Just solve some issues.")
class Action1(PostDeployActionBase):
    def execute(self):
        warnings.warn("START SOMEDEPLOYACTION")
        sleep(30)
        warnings.warn("END SOMEDEPLOYACTION")


@register_post_deploy(description="Just solve some more issues.")
class Action2(PostDeployActionBase):
    def execute(self):
        warnings.warn("START SOMEDEPLOYACTION")
        sleep(30)
        warnings.warn("END SOMEDEPLOYACTION")


@register_post_deploy(auto=False, description="Just solve some more issues.")
class Action3(PostDeployActionBase):
    def execute(self):
        warnings.warn("START SOMEDEPLOYACTION")
        sleep(30)
        warnings.warn("END SOMEDEPLOYACTION")
