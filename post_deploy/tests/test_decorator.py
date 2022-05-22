from unittest import mock

from django.test.testcases import TestCase


class TestDecoratorTestCase(TestCase):

    def tearDown(self):
        from post_deploy.utils import register_post_deploy
        register_post_deploy.bindings.clear()

    @mock.patch('post_deploy.utils.register_post_deploy.register_input')
    def test_plain_decorator(self, mocked_register_input):
        from post_deploy.utils import register_post_deploy

        @register_post_deploy
        def test_method_1():
            pass

        registered_names = [arg.__name__ for arg in mocked_register_input.mock_calls[0].args]
        self.assertIn('test_method_1', registered_names)

    @mock.patch('post_deploy.utils.register_post_deploy.register_input')
    def test_noargs_decorator(self, mocked_register_input):
        from post_deploy.utils import register_post_deploy

        @register_post_deploy()
        def test_method_2():
            pass

        registered_names = [arg.__name__ for arg in mocked_register_input.mock_calls[0].args]
        self.assertIn('test_method_2', registered_names)

    def test_auto_false_decorator(self):
        from post_deploy.utils import register_post_deploy

        @register_post_deploy(auto=False)
        def test_method_3():
            pass

        self.assertIn('post_deploy.test_method_3', register_post_deploy.bindings)
        self.assertFalse(register_post_deploy.bindings['post_deploy.test_method_3']['auto'])

    def test_auto_true_when_empty_decorator(self):
        from post_deploy.utils import register_post_deploy

        @register_post_deploy
        def test_method_4():
            pass

        @register_post_deploy()
        def test_method_5():
            pass

        @register_post_deploy()
        def test_method_6(auto=True):
            pass

        self.assertIn('post_deploy.test_method_4', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.test_method_4']['auto'])

        self.assertIn('post_deploy.test_method_5', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.test_method_5']['auto'])

        self.assertIn('post_deploy.test_method_6', register_post_deploy.bindings)
        self.assertTrue(register_post_deploy.bindings['post_deploy.test_method_6']['auto'])
