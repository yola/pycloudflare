from mock import patch

from pycloudflare.models import User, ZoneSettings
from tests.models import FakedServiceTestCase


class TestZoneSettings(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_zone_has_settings(self):
        self.assertIsInstance(self.zone.settings, ZoneSettings)

    def test_has_always_online_key(self):
        self.assertEqual(self.zone.settings['always_online'], 'on')

    def test_has_minify_key(self):
        self.assertEqual(self.zone.settings['minify'], {
            'css': 'off',
            'html': 'off',
            'js': 'off',
        })

    def test_doesnt_have_nonexistent_key(self):
        with self.assertRaises(KeyError):
            self.zone.settings['nonexistent_setting']

    def test_returns_setting_names_in_iteration(self):
        self.assertEqual(next(iter(self.zone.settings)), 'always_online')

    def test_updates_on_set(self):
        self.assertEqual(self.zone.settings['always_online'], 'on')
        self.zone.settings['always_online'] = 'off'
        self.assertEqual(self.zone.settings['always_online'], 'off')

    def test_can_set_when_uncached(self):
        self.assertEqual(self.zone.settings._settings, ())
        self.zone.settings['always_online'] = 'off'
        self.assertEqual(self.zone.settings['always_online'], 'off')

    def test_updates_setting_on_set(self):
        with patch.object(self.zone.service, 'set_zone_setting'):
            self.zone.settings['always_online'] = 'off'
            self.zone.service.set_zone_setting.assert_called_with(
                self.zone.id, 'always_online', 'off')
