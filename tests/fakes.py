from copy import deepcopy
from uuid import uuid4

from six import itervalues


class FakeHostService(object):
    def __init__(self):
        self.users = {
            'foo@example.net': {
                'cloudflare_email': 'foo@example.net',
                'cloudflare_username': 'foo',
                'unique_id': 'fake unique_id',
                'user_api_key': 'fake api_key',
                'user_key': 'fake user_key',
            },
        }

    def user_create(self, email, password, username=None, unique_id=None):
        self.users.setdefault(email, {
            'cloudflare_email': email,
            'cloudflare_username': username,
            'unique_id': unique_id,
            'user_api_key': 'fake api_key',
            'user_key': 'fake user_key',
        })
        return self.users[email].copy()

    def user_lookup(self, email=None, unique_id=None):
        if email:
            return self.users[email].copy()
        for user in itervalues(self.users):
            if unique_id == user.get('unique_id'):
                return user.copy()
        raise Exception('Not Found')

    def zone_set(self, zone_name, user_key, subdomains, resolve_to):
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
        return expected_response


class FakeService(object):
    def __init__(self, api_key, email):
        self.zones = {}
        self._add_zone('9a7806061c88ada191ed06f989cc3dac', 'example.com', True)
        self._add_zone('9a7806061c88ada191ed06f989cc3dbc', 'example.org', True)

    def _add_zone(self, id_, name, records=False):
        zone = {
            'id': id_,
            'name': name,
            'development_mode': 7200,
            'original_name_servers': [
                'ns1.originaldnshost.com',
                'ns2.originaldnshost.com',
            ],
            'original_registrar': 'GoDaddy',
            'original_dnshost': 'NameCheap',
            'created_on': '2014-01-01T05:20:00.12345Z',
            'modified_on': '2014-01-01T05:20:00.12345Z',
            'name_servers': [
                'tony.ns.cloudflare.com',
                'woz.ns.cloudflare.com',
            ],
            'owner': {
                'id': '9a7806061c88ada191ed06f989cc3dac',
                'email': 'user@example.com',
                'owner_type': 'user',
            },
            'permissions': [
                '#zone:read',
                '#zone:edit',
            ],
            'plan': {
                'id': '9a7806061c88ada191ed06f989cc3dac',
                'name': 'Pro Plan',
                'price': 20,
                'currency': 'USD',
                'frequency': 'monthly',
                'is_subscribed': True,
                'can_subscribe': True,
            },
            'status': 'active',
            'paused': False,
            'type': 'full',
            '_records': [
                {
                    'id': '9a7806061c88ada191ed06f989cc3dac',
                    'type': 'A',
                    'name': name,
                    'content': '1.2.3.4',
                    'proxiable': True,
                    'proxied': False,
                    'ttl': 120,
                    'locked': False,
                    'zone_id': id_,
                    'zone_name': name,
                    'created_on': '2014-01-01T05:20:00.12345Z',
                    'modified_on': '2014-01-01T05:20:00.12345Z',
                    'data': {},
                },
            ] if records else [],
            '_settings': {
                'always_online': {
                    'id': 'always_online',
                    'value': 'on',
                    'editable': True,
                    'modified_on': '2014-01-01T05:20:00.12345Z',
                },
                'minify': {
                    'id': 'minify',
                    'value': {
                        'css': 'off',
                        'html': 'off',
                        'js': 'off',
                    },
                    'editable': True,
                    'modified_on': '2014-01-01T05:20:00.12345Z',
                },
                'ssl': {'id': 'ssl', 'editable': True},
            },
            '_page_rules': [
                {
                    'id': '9a7806061c88ada191ed06f989cc3dac',
                    'targets': [{
                        'target': 'url',
                        'constraint': {
                          'operator': 'matches',
                          'value': '*example.com/images/*',
                        },
                    }],
                    'actions': [{
                        'id': 'always_online',
                        'value': 'on',
                    }],
                    'priority': 1,
                    'status': 'active',
                    'modified_on': '2014-01-01T05:20:00.12345Z',
                    'created_on': '2014-01-01T05:20:00.12345Z',
                },
            ],
        }
        self.zones[id_] = zone
        return zone

    def _clean_zone(self, zone):
        zone = deepcopy(zone)
        zone.pop('_records')
        zone.pop('_settings')
        return zone

    def get_zones(self, page=1, per_page=50):
        page -= 1  # Map to our 0-indexed list
        def iter_zones():
            for zone in list(self.zones.values())[page:page + per_page]:
                yield self._clean_zone(zone)
        return list(iter_zones())

    def get_zone_by_name(self, name):
        for zone in itervalues(self.zones):
            if zone['name'] == name:
                return self._clean_zone(zone)
        raise Exception('Not Found')

    def get_ssl_verification_info(self, zone_id):
        return 'ssl_verification_info'

    def create_zone(self, name, jump_start=False, organization=None):
        zone = self._add_zone(uuid4().hex, name)
        return self._clean_zone(zone)

    def delete_zone(self, zone_id):
        del self.zones[zone_id]

    def get_zone_settings(self, zone_id, page=1, per_page=50):
        page -= 1  # Map to our 0-indexed list
        settings = list(self.zones[zone_id]['_settings'].values())
        return deepcopy(settings[page:page + per_page])

    def set_zone_settings(self, zone_id, items):
        for setting in items:
            self.zones[zone_id]['_settings'][setting['id']].update(setting)
        return deepcopy(self.zones[zone_id]['_settings'])

    def create_dns_record(self, zone_id, data):
        data.update({
            'id': uuid4().hex,
            'proxiable': True,
            'locked': False,
            'zone_id': zone_id,
            'zone_name': self.zones[zone_id]['name'],
            'created_on': '2014-01-01T05:20:00.12345Z',
            'modified_on': '2014-01-01T05:20:00.12345Z',
        })
        data.setdefault('data', {})
        self.zones[zone_id]['_records'].append(data)
        return deepcopy(data)

    def _get_object(self, key, zone_id, page, per_page):
        page -= 1  # Map to our 0-indexed list
        return deepcopy(self.zones[zone_id][key][page:page + per_page])

    def _delete_object(self, key, zone_id, object_id):
        objects = [obj for obj in self.zones[zone_id][key]
                   if obj['id'] != object_id]
        if len(objects) == len(self.zones[zone_id][key]):
            raise Exception('Not Found')
        self.zones[zone_id][key] = objects

    def _update_object(self, key, zone_id, object_id, data):
        for obj in self.zones[zone_id][key]:
            if obj['id'] == object_id:
                break
        else:
            raise Exception('Not Found')
        obj.update(data)
        return deepcopy(obj)

    def get_dns_records(self, zone_id, page=1, per_page=50):
        return self._get_object('_records', zone_id, page, per_page)

    def delete_dns_record(self, zone_id, record_id):
        return self._delete_object('_records', zone_id, record_id)

    def update_dns_record(self, zone_id, record_id, data):
        return self._update_object('_records', zone_id, record_id, data)

    def create_page_rule(self, zone_id, data):
        data.update({
            'id': uuid4().hex,
            'created_on': '2014-01-01T05:20:00.12345Z',
            'modified_on': '2014-01-01T05:20:00.12345Z',
        })
        self.zones[zone_id]['_page_rules'].append(data)
        return deepcopy(data)

    def get_page_rules(self, zone_id, page=1, per_page=50):
        return self._get_object('_page_rules', zone_id, page, per_page)

    def delete_page_rule(self, zone_id, page_rule_id):
        return self._delete_object('_page_rules', zone_id, page_rule_id)

    def update_page_rule(self, zone_id, page_rule_id, data):
        return self._update_object('_page_rules', zone_id, page_rule_id, data)

    def purge_cache(self, zone_id, files=None, tags=None):
        return
