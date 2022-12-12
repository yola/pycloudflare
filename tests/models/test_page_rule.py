from copy import deepcopy

from mock import patch
from six import string_types

from pycloudflare.models import PageRule, User
from tests.models import FakedServiceTestCase


class TestCreatePageRule(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.page_rule = self.zone.create_page_rule(
            url_matches='example.net/*',
            actions=[{'id': 'always_online', 'value': 'on'}])

    def test_returns_page_rule_object(self):
        self.assertIsInstance(self.page_rule, PageRule)

    def test_has_id_attribute(self):
        self.assertIsInstance(self.page_rule.id, string_types)

    def test_has_targets_attribute(self):
        self.assertEqual(self.page_rule.targets, [{
            'target': 'url',
            'constraint': {
                'operator': 'matches',
                'value': 'example.net/*',
            },
        }])

    def test_has_actions_attribute(self):
        self.assertEqual(self.page_rule.actions, [{
            'id': 'always_online',
            'value': 'on',
        }])

    def test_has_priority_attribute(self):
        self.assertEqual(self.page_rule.priority, 1)

    def test_has_status_attribute(self):
        self.assertEqual(self.page_rule.status, 'active')

    def test_doesnt_have_nonexistent_attribute(self):
        with self.assertRaises(AttributeError):
            self.page_rule.nonexistent

    def test_repr_able(self):
        self.assertTrue(repr(self.page_rule).startswith('PageRule <'))

    def test_invalidates_zone_records(self):
        old_page_rules = self.zone.page_rules
        self.zone.create_page_rule(
            url_matches='example.net/foo',
            actions=[{'id': 'always_online', 'value': 'off'}])
        self.assertNotEqual(old_page_rules, self.zone.page_rules)


class TestVerbosePageRule(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')

    def test_creates_rule(self):
        page_rule = self.zone.create_page_rule(
            targets=[{
                'target': 'url',
                'constraint': {
                    'operator': 'matches',
                    'value': 'example.net/bar',
                }
            }],
            actions=[{
                'id': 'always_online',
                'value': 'on',
            }],
            priority=1,
            status='active',
        )
        self.assertIsInstance(page_rule, PageRule)

    def test_rejects_targets_and_url_matches(self):
        with self.assertRaises(ValueError):
            self.zone.create_page_rule(
                targets=[{
                    'target': 'url',
                    'constraint': {
                        'operator': 'matches',
                        'value': 'example.net/foo',
                    }
                }],
                url_matches='example.net/bar',
                actions=[{
                    'id': 'always_online',
                    'value': 'on',
                }],
            )


class TestDeletePageRule(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.page_rule = self.zone.page_rules[0]

    def test_can_delete(self):
        self.page_rule.delete()
        self.assertEqual(self.zone.page_rules, [])


class TestUpdatePageRule(FakedServiceTestCase):
    def setUp(self):
        self.user = User.get(email='foo@example.net')
        self.zone = self.user.get_zone_by_name('example.com')
        self.page_rule = self.zone.page_rules[0]

    def test_unknown_attribute_sets_are_rejected(self):
        with self.assertRaises(AttributeError):
            self.page_rule.unknown_attribute = True

    def test_pending_changes_are_visible(self):
        self.page_rule.status = 'disabled'
        self.assertEqual(self.page_rule.status, 'disabled')

    def test_save_without_changes_is_noop(self):
        with patch.object(self.page_rule._service, 'update_page_rule'):
            self.page_rule.save()
            self.assertEqual(
                self.page_rule._service.update_page_rule.call_count, 0)

    def test_save_performs_update(self):
        self.page_rule.actions[0]['value'] = 'off'
        page_rule_id = self.page_rule.id
        page_rule_data = deepcopy(self.page_rule._data)
        with patch.object(self.page_rule._service, 'update_page_rule'):
            self.page_rule.save()
            self.page_rule._service.update_page_rule.assert_called_with(
                self.zone.id, page_rule_id, page_rule_data)

    def test_invalidates_page_rules_on_priority_change(self):
        old_page_rules = self.zone.page_rules
        self.page_rule.priority = 42
        self.page_rule.save()
        self.assertIsNot(self.zone.page_rules, old_page_rules)
