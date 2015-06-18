from copy import deepcopy
from uuid import uuid4


class FakeHostService(object):
    users = {
        'foo@example.net': {
            'cloudflare_email': 'foo@example.net',
            'cloudflare_username': 'foo',
            'unique_id': 'fake unique_id',
            'user_api_key': 'fake api_key',
            'user_key': 'fake user_key',
        },
    }

    def __init__(self, users=None):
        self.users = users or FakeHostService.users.copy()

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
        for user in self.users.itervalues():
            if unique_id == user.get('unique_id'):
                return user.copy()
        raise Exception('Not Found')


def simple_zone(id_, name, records=False):
    return id_, {
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
        },
    }


class FakeService(object):
    zones = dict((
        simple_zone('9a7806061c88ada191ed06f989cc3dac', 'example.com', True),
    ))

    def __init__(self, email, api_key, zones=None):
        self.zones = zones or deepcopy(FakeService.zones)

    def _clean_zone(self, zone):
        zone = deepcopy(zone)
        zone.pop('_records')
        zone.pop('_settings')
        return zone

    def iter_zones(self):
        for zone in self.zones.itervalues():
            yield self._clean_zone(zone)

    def get_zone_by_name(self, name):
        for zone in self.zones.itervalues():
            if zone['name'] == name:
                return self._clean_zone(zone)
        raise Exception('Not Found')

    def create_zone(self, name, jump_start=False):
        id_, zone = simple_zone(uuid4().hex, name)
        self.zones[id_] = zone
        return self._clean_zone(zone)

    def delete_zone(self, zone_id):
        del self.zones[zone_id]

    def get_zone_settings(self, zone_id):
        return deepcopy(self.zones[zone_id]['_settings'])

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
            'data': {},
        })
        self.zones[zone_id]['_records'].append(data)
        return deepcopy(data)

    def iter_dns_records(self, zone_id):
        for record in self.zones[zone_id]['_records']:
            yield deepcopy(record)

    def delete_dns_record(self, zone_id, record_id):
        records = [record for record in self.zones[zone_id]['_records']
                   if record['id'] != record_id]
        if len(records) == len(self.zones[zone_id]['_records']):
            raise Exception('Not Found')
        self.zones[zone_id]['_records'] = records

    def update_dns_record(self, zone_id, record_id, data):
        for record in self.zones[zone_id]['_records']:
            if record['id'] == record_id:
                break
        else:
            raise Exception('Not Found')
        record.update(data)
        return deepcopy(record)