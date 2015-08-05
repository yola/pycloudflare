from six import string_types

from pycloudflare.models import Record, User, Zone
from tests.models import FakedServiceTestCase


class TestCreateZone(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.create_zone('example.net')

    def test_returns_zone_object(self):
        self.assertIsInstance(self.zone, Zone)

    def test_has_correct_name(self):
        self.assertEqual(self.zone.name, 'example.net')

    def test_has_id(self):
        self.assertIsInstance(self.zone.id, string_types)

    def test_has_name_servers(self):
        self.assertEqual(self.zone.name_servers,
                         ['tony.ns.cloudflare.com', 'woz.ns.cloudflare.com'])

    def test_has_type(self):
        self.assertEqual(self.zone.type, 'full')

    def test_has_status(self):
        self.assertEqual(self.zone.status, 'active')

    def test_has_paused(self):
        self.assertFalse(self.zone.paused)

    def test_has_development_mode(self):
        self.assertEqual(self.zone.development_mode, 7200)

    def test_has_owner(self):
        self.assertIsInstance(self.zone.owner, dict)
        self.assertEqual(self.zone.owner['id'],
                         '9a7806061c88ada191ed06f989cc3dac')

    def test_has_permissions(self):
        self.assertIsInstance(self.zone.permissions, list)

    def test_has_plan(self):
        self.assertIsInstance(self.zone.plan, dict)

    def test_repr_able(self):
        self.assertEqual(repr(self.zone), 'Zone<example.net>')


class TestDeleteZone(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')

    def test_deletes_zone(self):
        self.assertNotEqual(self.user.zones, [])
        zone = self.user.get_zone_by_name('example.com')
        zone.delete()
        self.assertEqual(self.user.zones, [])


class TestZoneRecords(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_iter_records_yields_record_objects(self):
        record = next(self.zone.iter_records())
        self.assertIsInstance(record, Record)

    def test_records_lists_records_by_name(self):
        self.assertIsInstance(self.zone.records, dict)
        self.assertIsInstance(self.zone.records['example.com'], list)
        self.assertIsInstance(self.zone.records['example.com'][0], Record)
