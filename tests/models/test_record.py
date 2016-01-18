from copy import deepcopy

from mock import patch
from six import string_types

from pycloudflare.models import Record, User
from tests.models import FakedServiceTestCase


class TestCreateRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.create_record(
            'bar.example.com', 'A', '127.0.0.1')

    def test_returns_record_object(self):
        self.assertIsInstance(self.record, Record)

    def test_has_id_attribute(self):
        self.assertIsInstance(self.record.id, string_types)

    def test_has_type_attribute(self):
        self.assertEqual(self.record.type, 'A')

    def test_has_name_attribute(self):
        self.assertEqual(self.record.name, 'bar.example.com')

    def test_has_content_attribute(self):
        self.assertEqual(self.record.content, '127.0.0.1')

    def test_has_proxiable_attribute(self):
        self.assertEqual(self.record.proxiable, True)

    def test_has_proxied_attribute(self):
        self.assertEqual(self.record.proxied, False)

    def test_has_ttl_attribute(self):
        self.assertEqual(self.record.ttl, 1)

    def test_has_locked_attribute(self):
        self.assertEqual(self.record.locked, False)

    def test_has_data_attribute(self):
        self.assertEqual(self.record.data, {})

    def test_doesnt_have_nonexistent_attribute(self):
        with self.assertRaises(AttributeError):
            self.record.nonexistent

    def test_repr_able(self):
        self.assertEqual(
            repr(self.record), 'Record<bar.example.com 1 IN A 127.0.0.1>')

    def test_invalidates_zone_records(self):
        self.assertNotIn('baz.example.com', self.zone.records)
        self.zone.create_record('baz.example.com', 'A', '127.0.0.1')
        self.assertIn('baz.example.com', self.zone.records)
        self.zone.create_record('baz.example.com', 'A', '127.0.0.2')
        self.assertEqual(len(self.zone.records['baz.example.com']), 2)


class TestCreateMXRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_sets_priority(self):
        record = self.zone.create_record('bar.example.com', 'MX', 'mail.net',
                                         priority=10)
        self.assertEqual(record.priority, 10)


class TestCreateSRVRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.test_record = self.zone.create_record(
            'bar.example.com', 'SRV', priority=10, weight=5,
            service='_sip', protocol='_tcp', port=8806, target='example.net'
        )

    def test_sets_priority(self):
        self.assertEqual(self.test_record.data['priority'], 10)

    def test_sets_weight(self):
        self.assertEqual(self.test_record.data['weight'], 5)

    def test_sets_service(self):
        self.assertEqual(self.test_record.data['service'], '_sip')

    def test_sets_protocol(self):
        self.assertEqual(self.test_record.data['proto'], '_tcp')

    def test_sets_port(self):
        self.assertEqual(self.test_record.data['port'], 8806)

    def test_sets_target(self):
        self.assertEqual(self.test_record.data['target'], 'example.net')


class TestDeleteRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.records['example.com'][0]

    def test_can_delete(self):
        self.record.delete()
        self.assertEqual(self.zone.records, {})


class TestUpdateRecord(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.record = self.zone.records['example.com'][0]

    def test_unknown_attribute_sets_are_rejected(self):
        with self.assertRaises(AttributeError):
            self.record.unknown_attribute = True

    def test_pending_changes_are_visible(self):
        self.record.proxied = True
        self.assertEqual(self.record.proxied, True)

    def test_save_without_changes_is_noop(self):
        with patch.object(self.record._service, 'update_dns_record'):
            self.record.save()
            self.assertEqual(
                self.record._service.update_dns_record.call_count, 0)

    def test_save_performs_update(self):
        self.record.proxied = True
        record_id = self.record.id
        record_data = deepcopy(self.record._data)
        with patch.object(self.record._service, 'update_dns_record'):
            self.record.save()
            self.record._service.update_dns_record.assert_called_with(
                self.zone.id, record_id, record_data)

    def test_invalidates_zone_records_on_rename(self):
        self.assertNotIn('quux.example.com', self.zone.records)
        self.record.name = 'quux.example.com'
        self.record.save()
        self.assertIn('quux.example.com', self.zone.records)
