import os
import types
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

    def test_get_all_zones(self):
        zones = self.cloudflare.iter_zones()
        self.assertIsInstance(zones, types.GeneratorType)

    def test_get_zone(self):
        zone_id = self.cloudflare.get_zones()[0]['id']
        zone = self.cloudflare.get_zone(zone_id)
        self.assertIsInstance(zone, dict)
