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
        self.assertEqual(self.zone.settings.always_online, 'on')

    def test_has_minify_key(self):
        self.assertEqual(self.zone.settings.minify, {
            'css': 'off',
            'html': 'off',
            'js': 'off',
        })

    def test_doesnt_have_nonexistent_key(self):
        with self.assertRaises(AttributeError):
            self.zone.settings.nonexistent_setting

    def test_repr_able(self):
        self.assertEqual(repr(self.zone.settings), 'ZoneSettings<example.com>')

    def test_returns_setting_names_in_iteration(self):
        self.assertEqual(next(iter(self.zone.settings)), 'always_online')

    def test_rejects_unknown_settings_writes(self):
        with self.assertRaises(AttributeError):
            self.zone.settings.nonexistent_setting = True

    def test_pending_changes_are_visible(self):
        self.assertEqual(self.zone.settings.always_online, 'on')
        self.zone.settings.always_online = 'off'
        self.assertEqual(self.zone.settings.always_online, 'off')

    def test_save_without_changes_is_noop(self):
        with patch.object(self.zone._service, 'set_zone_settings'):
            self.zone.settings.save()
            self.assertEqual(
                self.zone._service.set_zone_settings.call_count, 0)

    def test_save_performs_update(self):
        self.zone.settings.always_online = 'off'
        with patch.object(self.zone._service, 'set_zone_settings'):
            self.zone.settings.save()
            self.zone._service.set_zone_settings.assert_called_with(
                self.zone.id, [{'id': 'always_online', 'value': 'off'}])
