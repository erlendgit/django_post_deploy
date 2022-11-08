from unittest import mock

from django.test.testcases import TestCase


def test_method_1():
    pass


def test_method_2():
    pass


def test_method_3():
    pass


def test_method_4():
    pass


def test_method_5():
    pass


def test_method_6():
    pass


class TestDecoratorTestCase(TestCase):

    def tearDown(self):
        from post_deploy.utils import register_post_deploy
        register_post_deploy.bindings.clear()

    @mock.patch('post_deploy.utils.register_post_deploy.register_input')
    def test_plain_decorator(self, mocked_register_input):
        from post_deploy.utils import register_post_deploy

        register_post_deploy(test_method_1)

        registered_names = [arg.__name__ for arg in mocked_register_input.mock_calls[0].args]
        self.assertIn('test_method_1', registered_names)

    @mock.patch('post_deploy.utils.register_post_deploy.register_input')
    def test_noargs_decorator(self, mocked_register_input):
        from post_deploy.utils import register_post_deploy

        register_post_deploy()(test_method_2)

        registered_names = [arg.__name__ for arg in mocked_register_input.mock_calls[0].args]
        self.assertIn('test_method_2', registered_names)

    def test_auto_false_decorator(self):
        from post_deploy.utils import register_post_deploy

        register_post_deploy(auto=False)(test_method_3)

        ID = 'post_deploy.tests.test_decorator.test_method_3'
        self.assertIn(ID, register_post_deploy.bindings)
        self.assertFalse(register_post_deploy.bindings[ID]['auto'])

    def test_auto_true_when_empty_decorator(self):
        from post_deploy.utils import register_post_deploy

        register_post_deploy()(test_method_4)

        register_post_deploy()(test_method_5)

        register_post_deploy(auto=True)(test_method_6)

        self.assertIn('post_deploy.tests.test_decorator.test_method_4', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.tests.test_decorator.test_method_4']['auto'])

        self.assertIn('post_deploy.tests.test_decorator.test_method_5', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.tests.test_decorator.test_method_5']['auto'])

        self.assertIn('post_deploy.tests.test_decorator.test_method_6', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.tests.test_decorator.test_method_6']['auto'])
