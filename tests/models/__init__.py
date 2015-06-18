from unittest import TestCase

from mock import patch

from tests.fakes import FakeHostService, FakeService


class FakedServiceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host_service_patcher = patch(
            'pycloudflare.models.User.get_host_service',
            side_effect=FakeHostService)
        cls.host_service_patcher.start()

        cls.service_patcher = patch(
            'pycloudflare.models.User.get_service',
            side_effect=FakeService)
        cls.service_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.host_service_patcher.stop()
        cls.service_patcher.stop()
