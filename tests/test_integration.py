import os
from unittest import TestCase

from demands import HTTPServiceError
from yoconfigurator.base import read_config
from yoconfig import configure_services

from pycloudflare.services import CloudFlareService

app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
conf = read_config(app_dir)
configure_services('cloudflare', ['cloudflare'], conf.common)


class ZonesTest(TestCase):
    def setUp(self):
        self.cf = CloudFlareService()

    def test_iter_zones(self):
        zone = next(self.cf.iter_zones())
        self.assertIsInstance(zone, dict)


class ZoneTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cf = CloudFlareService()
        cls.zone_name = 'example.net'
        try:
            zone = cls.cf.create_zone(cls.zone_name)
        except HTTPServiceError:
            zone = cls.cf.get_zone_by_name(cls.zone_name)
        cls.zone_id = zone['id']

    @classmethod
    def tearDownClass(cls):
        cls.cf.delete_zone(cls.zone_id)

    def test_get_zone(self):
        zone = self.cf.get_zone(self.zone_id)
        self.assertIsInstance(zone, dict)

    def test_get_zone_by_name(self):
        zone = self.cf.get_zone_by_name(self.zone_name)
        self.assertEqual(zone['id'], self.zone_id)
