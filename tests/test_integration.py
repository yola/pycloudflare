import os
from unittest import TestCase

from yoconfigurator.base import read_config
from yoconfig import configure_services

from pycloudflare.services import CloudFlareService

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
conf = read_config(app_dir)


class ZonesTest(TestCase):
    def setUp(self):
        configure_services('cloudflare', ['cloudflare'], conf.common)
        self.cloudflare = CloudFlareService()

    def test_iter_zones(self):
        zone = next(self.cloudflare.iter_zones())
        self.assertIsInstance(zone, dict)

    def test_get_zone(self):
        zone_id = next(self.cloudflare.iter_zones())['id']
        zone = self.cloudflare.get_zone(zone_id)
        self.assertIsInstance(zone, dict)

    def test_get_resource_records(self):
        zone_id = next(self.cloudflare.iter_zones())['id']
        resource_records = self.cloudflare.get_resource_records(zone_id)
        self.assertIsInstance(resource_records, list)
