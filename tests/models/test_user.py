from pycloudflare.models import User, Zone
from tests.models import FakedServiceTestCase


class UserAttributeTestsMixin(object):
    def test_sets_email_attribute(self):
        self.assertEqual(self.user.email, 'foo@example.net')

    def test_sets_service_attribute(self):
        self.assertTrue(self.user._service)

    def test_repr_able(self):
        self.assertEqual(repr(self.user), 'User<foo@example.net>')


class TestUserInstantiate(FakedServiceTestCase, UserAttributeTestsMixin):
    def setUp(self):
        self.user = User(email='foo@example.net', api_key='fake api_key')


class TestUserCreate(FakedServiceTestCase, UserAttributeTestsMixin):
    def setUp(self):
        self.user = User.get_or_create('foo@example.net', 'bar', 'foo',
                                       'fake unique_id')

    def test_has_user_key(self):
        self.assertEqual(self.user.user_key, 'fake user_key')


class TestUserGet(FakedServiceTestCase, UserAttributeTestsMixin):
    def setUp(self):
        self.user = User.get(email='foo@example.net')

    def test_get_by_unique_id(self):
        self.assertTrue(User.get(unique_id='fake unique_id'))


class TestUserZones(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')

    def test_iter_zones_returns_zone_objects(self):
        zone = next(self.user.iter_zones())
        self.assertIsInstance(zone, Zone)

    def test_zones_returns_zone_objects(self):
        zone = self.user.zones[0]
        self.assertIsInstance(zone, Zone)

    def test_get_zone_by_name_returns_zone_objects(self):
        zone = self.user.get_zone_by_name('example.com')
        self.assertIsInstance(zone, Zone)
