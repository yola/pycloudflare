from unittest import TestCase
from uuid import uuid4

from demands import HTTPServiceError

from pycloudflare.models import User
from pycloudflare.services import (
    CloudFlareHostPageIterator, CloudFlareHostService, CloudFlarePageIterator,
    CloudFlareService, ZoneNotFound)


TEST_USER = {}


def setUpModule():
    cfh = CloudFlareHostService()
    TEST_USER['password'] = uuid4().hex
    TEST_USER['unique_id'] = uuid4().hex
    TEST_USER['email'] = '%s@integrationtest.example.net' % uuid4().hex
    r = cfh.user_create(email=TEST_USER['email'],
                        password=TEST_USER['password'],
                        unique_id=TEST_USER['unique_id'])
    TEST_USER['api_key'] = r['user_api_key']


def tearDownModule():
    cf = cf_service()
    for zone in CloudFlarePageIterator(cf.get_zones):
        cf.delete_zone(zone['id'])


def cf_service():
    return CloudFlareService(email=TEST_USER['email'],
                             api_key=TEST_USER['api_key'])


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
            for record in CloudFlarePageIterator(
                    cls.cf.get_dns_records, args=(cls.zone_id,)):
                if record['name'] == 'foo.example.net':
                    break
        cls.record_id = record['id']

    @classmethod
    def tearDownClass(cls):
        cls.cf.delete_zone(cls.zone_id)

    def test_get_zones(self):
        zone = self.cf.get_zones()[0]
        self.assertIsInstance(zone, dict)

    def test_get_zone(self):
        zone = self.cf.get_zone(self.zone_id)
        self.assertIsInstance(zone, dict)

    def test_get_zone_by_name(self):
        zone = self.cf.get_zone_by_name(self.zone_name)
        self.assertEqual(zone['id'], self.zone_id)

    def test_get_zone_by_name_raises_exception(self):
        self.assertRaises(ZoneNotFound, self.cf.get_zone_by_name, 'foo.bar')

    def test_get_zone_settings(self):
        settings = self.cf.get_zone_settings(self.zone_id)
        for setting in settings:
            if setting['id'] == 'always_online':
                self.assertIn(setting['value'], ('on', 'off'))
                return
        raise AssertionError('Expected to find always_online setting')

    def test_set_zone_settings(self):
        settings = self.cf.set_zone_settings(self.zone_id, [
            {'id': 'always_online', 'value': 'on'},
            {'id': 'ipv6', 'value': 'on'},
        ])
        self.assertIsInstance(settings, list)
        self.assertIn(settings[0]['id'], ('always_online', 'ipv6'))
        self.assertEqual(settings[0]['value'], 'on')

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


class HostZonesTest(TestCase):
    def setUp(self):
        self.cfh = CloudFlareHostService()
        self.user = self.cfh.user_lookup(email=TEST_USER['email'])

    def test_zone_list(self):
        zones = CloudFlareHostPageIterator(self.cfh.zone_list)
        try:
            zone = next(iter(zones))
        except StopIteration:
            pass
        else:
            self.assertIsInstance(zone, dict)

    def test_full_zone_set(self):
        response = self.cfh.full_zone_set('example.org', self.user['user_key'])
        self.assertIsInstance(response, dict)


class HostUserTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfh = CloudFlareHostService()
        cls.email = TEST_USER['email']
        cls.password = TEST_USER['password']
        cls.unique_id = TEST_USER['unique_id']

    def test_user_lookup_by_email(self):
        user = self.cfh.user_lookup(email=self.email)
        self.assertIsInstance(user, dict)

    def test_user_lookup_by_unique_id(self):
        user = self.cfh.user_lookup(unique_id=self.unique_id)
        self.assertIsInstance(user, dict)

    def test_user_create(self):
        user = self.cfh.user_create(self.email, self.password,
                                    unique_id=self.unique_id)
        self.assertIsInstance(user, dict)

    def test_error_handler(self):
        with self.assertRaises(HTTPServiceError):
            self.cfh.user_create('not_an_email_address', None)


class CreateHostZoneTest(TestCase):
    def setUp(self):
        user = User(TEST_USER['email'], TEST_USER['api_key'])
        self.zone = user.create_host_zone('example{}.com'.format(uuid4().hex))

    def test_creates_zone_without_any_records(self):
        self.assertEqual(self.zone.records, {})
