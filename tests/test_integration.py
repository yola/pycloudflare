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

    def test_get_all_zones(self):
        zones = self.cloudflare.get_zones()
        self.assertIsInstance(zones, list)

    def test_get_zone(self):
        zone = self.cloudflare.get_zones()[0]
        self.assertIsInstance(zone, dict)
