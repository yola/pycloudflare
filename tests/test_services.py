from mock import patch
from unittest import TestCase

from pycloudflare.services import CloudFlareService


class TestPurgeZoneCache(TestCase):

    def setUp(self):
        self.delete_mock = patch(
            'pycloudflare.services.CloudFlareService.delete').start()

    def tearDown(self):
        self.delete_mock.stop()

    def test_full_purge(self):
        CloudFlareService('api_key', 'email').purge_cache('zone_id')
        self.delete_mock.assert_called_once_with(
            'zones/zone_id/purge_cache', json={'purge_everything': True})

    def test_partial_purge(self):
        CloudFlareService('api_key', 'email').purge_cache(
            'zone_id', hosts=['h1', 'h2'], tags=['t1', 't2'])
        self.delete_mock.assert_called_once_with(
            'zones/zone_id/purge_cache',
            json={'hosts': ['h1', 'h2'], 'tags': ['t1', 't2']}
        )
