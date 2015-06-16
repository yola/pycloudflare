import os
from unittest import TestCase

from demands import HTTPServiceError
from yoconfigurator.base import read_config
from yoconfig import configure_services

from pycloudflare.services import CloudFlareService


def cf_service():
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    conf = read_config(app_dir)
    configure_services('cloudflare', ['cloudflare'], conf.common)
    # TODO: Create a test account via the partner API
    client_conf = conf.common.cloudflare.yola_other_domains
    return CloudFlareService(api_key=client_conf.api_key,
                             email=client_conf.email)


class ZonesTest(TestCase):
    def setUp(self):
        self.cf = cf_service()

    def test_iter_zones(self):
        zone = next(self.cf.iter_zones())
        self.assertIsInstance(zone, dict)


class ZoneTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cf = cf_service()
        cls.zone_name = 'example.net'
        try:
            zone = cls.cf.create_zone(cls.zone_name)
        except HTTPServiceError:
            zone = cls.cf.get_zone_by_name(cls.zone_name)
        cls.zone_id = zone['id']
        try:
            record = cls.cf.create_dns_record(cls.zone_id, {
                'name': 'foo.example.net',
                'type': 'A',
                'content': '127.0.0.1',
                'proxied': False,
                'ttl': 1,
            })
        except HTTPServiceError:
            for record in cls.cf.iter_dns_records(cls.zone_id):
                if record['name'] == 'foo.example.net':
                    break
        cls.record_id = record['id']

    @classmethod
    def tearDownClass(cls):
        cls.cf.delete_zone(cls.zone_id)

    def test_get_zone(self):
        zone = self.cf.get_zone(self.zone_id)
        self.assertIsInstance(zone, dict)

    def test_get_zone_by_name(self):
        zone = self.cf.get_zone_by_name(self.zone_name)
        self.assertEqual(zone['id'], self.zone_id)

    def test_get_zone_settings(self):
        settings = self.cf.get_zone_settings(self.zone_id)
        self.assertIn('always_online', settings)
        self.assertIn(settings['always_online']['value'], ('on', 'off'))

    def test_get_zone_setting(self):
        setting = self.cf.get_zone_setting(self.zone_id, 'always_online')
        self.assertIn('value', setting)
        self.assertIn(setting['value'], ('on', 'off'))

    def test_set_zone_setting(self):
        setting = self.cf.set_zone_setting(self.zone_id, 'always_online', 'on')
        self.assertIn('value', setting)
        self.assertEqual(setting['value'], 'on')

    def test_get_dns_records(self):
        records = self.cf.get_dns_records(self.zone_id)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['content'], '127.0.0.1')

    def test_get_dns_record(self):
        record = self.cf.get_dns_record(self.zone_id, self.record_id)
        self.assertEqual(record['content'], '127.0.0.1')

    def test_update_dns_record(self):
        record = self.cf.update_dns_record(
            self.zone_id, self.record_id, {'content': '127.0.0.2'})
        self.assertEqual(record['content'], '127.0.0.2')

    def test_create_delete_dns_record(self):
        record = self.cf.create_dns_record(self.zone_id, {
            'name': 'bar.example.net',
            'type': 'CNAME',
            'content': 'example.org',
            'proxied': True,
            'ttl': 1,
        })
        self.assertIsInstance(record, dict)
        self.cf.delete_dns_record(self.zone_id, record['id'])
