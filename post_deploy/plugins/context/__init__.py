from contextlib import contextmanager


class DefaultContext():

    def __init__(self, parameters):
        self.parameters = parameters or self.default_parameters()

    def default_parameters(self):
        return {}

    @contextmanager
    def execute(self):
        yield


