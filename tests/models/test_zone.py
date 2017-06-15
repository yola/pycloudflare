from mock import Mock
from six import string_types

from pycloudflare.exceptions import SSLUnavailable
from pycloudflare.models import PageRule, Record, User, Zone
from pycloudflare.services import HTTPServiceError
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
        zone = self.user.get_zone_by_name('example.org')
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


class TestZonePageRules(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_iter_page_rules_yields_page_rule_objects(self):
        page_rule = next(self.zone.iter_page_rules())
        self.assertIsInstance(page_rule, PageRule)

    def test_page_rules_returns_list_of_page_rule_objects(self):
        self.assertIsInstance(self.zone.page_rules, list)
        self.assertIsInstance(self.zone.page_rules[0], PageRule)


class TestSetCNameZone(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.result = self.user.create_cname_zone(
            'example.org', ['cname.example.org'], 'resolve-to.example.org')

    def test_returns_correct_data_from_service(self):
        expected_response = {
            'hosted_cnames': {
                'www.example.org': 'resolve-to.example.org'
            },
            'zone_name': 'example.org',
            'forward_tos': {
                'www.example.org': 'www.example.org.cdn.cloudflare.net'
            },
            'resolving_to': 'resolve-to.example.org'
        }
        self.assertEqual(self.result, expected_response)


class TestGetSSLVerificationInfoForZone(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        zone = self.user.create_cname_zone(
            'example.org', ['cname.example.org'], 'resolve-to.example.org')
        zone = self.user.get_zone_by_name('example.org')
        zone.settings.ssl = 'full'
        zone.settings.save()
        self.result = zone.get_ssl_verification_info()

    def test_ssl_verification_info_is_returned(self):
        self.assertEqual(self.result, 'ssl_verification_info')


class TestGetSSLVerificationInfoForZoneWithError(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        zone = self.user.create_cname_zone(
            'example.org', ['cname.example.org'], 'resolve-to.example.org')
        zone = self.user.get_zone_by_name('example.org')
        zone._service = Mock()

        data = {'errors': [{'code': 1001, 'msg': 'msg'}]}
        zone._service.get_ssl_verification_info.side_effect = (
            HTTPServiceError(response=Mock(json=Mock(return_value=data)))
        )
        self.zone = zone

    def test_proper_exception_is_raised(self):
        self.assertRaises(SSLUnavailable, self.zone.get_ssl_verification_info)


class TestPurgeZone(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_full_purge(self):
        self.zone.purge_cache()
