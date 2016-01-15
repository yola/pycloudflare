from copy import deepcopy

from property_caching import (
    cached_property, clear_property_cache, set_property_cache)
from six import iteritems, itervalues

from pycloudflare.services import (
    CloudFlareHostService, CloudFlarePageIterator, CloudFlareService)


class User(object):
    def __init__(self, email, api_key):
        self.email = email
        self._service = self.get_service(api_key, email)

    @classmethod
    def get_host_service(cls):
        return CloudFlareHostService()

    @classmethod
    def get_service(cls, api_key, email):
        return CloudFlareService(api_key, email)

    @classmethod
    def get_or_create(cls, email, password, username=None, unique_id=None):
        service = cls.get_host_service()
        data = service.user_create(email, password, username, unique_id)
        return cls.create_from_host_api_response(data)

    @classmethod
    def get(cls, email=None, unique_id=None):
        service = cls.get_host_service()
        data = service.user_lookup(email=email, unique_id=unique_id)
        return cls.create_from_host_api_response(data)

    @classmethod
    def create_from_host_api_response(cls, data):
        user = User(data['cloudflare_email'], data['user_api_key'])
        set_property_cache(user, '_host_api_data', data)
        return user

    @cached_property
    def _host_api_data(self):
        service = self.get_host_service()
        return service.user_lookup(email=self.email)

    @property
    def user_key(self):
        return self._host_api_data['user_key']

    @cached_property
    def zones(self):
        return list(self.iter_zones())

    def iter_zones(self):
        for zone in CloudFlarePageIterator(self._service.get_zones):
            yield Zone(self, zone)

    def get_zone_by_name(self, name):
        zone = self._service.get_zone_by_name(name)
        return Zone(self, zone)

    def create_host_zone(self, name, jump_start=False):
        host_service = self.get_host_service()
        host_service.full_zone_set(name, self.user_key, jump_start)
        zone = self.get_zone_by_name(name)

        # Zone created by using Host API contains some garbage records.
        # We should remove them before creating our owns.
        for record in zone.iter_records():
            record.delete()

        return zone

    def create_zone(self, name, jump_start=False, organization=None):
        zone = self._service.create_zone(name=name, jump_start=jump_start,
                                         organization=organization)
        return Zone(self, zone)

    def __repr__(self):
        return 'User<%s>' % self.email


class Zone(object):
    def __init__(self, user, data):
        self.user = user
        self._service = user._service
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError()

    def delete(self):
        self._service.delete_zone(self.id)
        clear_property_cache(self.user, 'zones')

    @cached_property
    def settings(self):
        return ZoneSettings(self)

    def iter_records(self):
        for record in CloudFlarePageIterator(
                self._service.get_dns_records, args=(self.id,)):
            yield Record(self, record)

    @cached_property
    def records(self):
        by_name = {}
        for record in self.iter_records():
            by_name.setdefault(record.name, []).append(record)
        for value in itervalues(by_name):
            value.sort(key=lambda r: (r.type, r.content))
        return by_name

    def create_record(self, name, record_type, content=None, ttl=1,
                      proxied=False, **kwargs):
        data = {
            'name': name,
            'type': record_type,
            'ttl': ttl,
            'proxied': proxied,
        }

        if content:
            data['content'] = content

        if record_type == 'MX':
            data['priority'] = kwargs['priority']
        elif record_type == 'SRV':
            data['data'] = {
                'name': name,
                'service': kwargs['service'],
                'proto': kwargs['protocol'],
                'priority': kwargs['priority'],
                'weight': kwargs['weight'],
                'port': kwargs['port'],
                'target': kwargs['target'],
            }

        record = self._service.create_dns_record(self.id, data)
        clear_property_cache(self, 'records')
        return Record(self, record)

    def __repr__(self):
        return 'Zone<%s>' % self.name


class ZoneSettings(object):
    def __init__(self, zone):
        self.zone = zone
        self._service = zone._service
        self._get_settings()
        self._updates = {}

    def _get_settings(self):
        self._settings = {}
        for setting in CloudFlarePageIterator(
                self._service.get_zone_settings, args=(self.zone.id,)):
            self._settings[setting['id']] = setting

    def __getattr__(self, name):
        if name in self._updates:
            return self._updates[name]
        if name in self._settings:
            return self._settings[name]['value']
        raise AttributeError()

    def __setattr__(self, name, value):
        if name in ('zone', '_service', '_settings', '_updates'):
            return super(ZoneSettings, self).__setattr__(name, value)
        if name not in self._settings:
            raise AttributeError('Not a valid setting')
        if not self._settings[name]['editable']:
            raise ValueError('Not an editeable setting')
        self._updates[name] = value

    def save(self):
        if not self._updates:
            return
        items = [{'id': name, 'value': value}
                 for name, value in iteritems(self._updates)]
        self._service.set_zone_settings(self.zone.id, items)
        self._get_settings()
        self._updates = {}

    def __iter__(self):
        return iter(sorted(self._settings))

    def __repr__(self):
        return 'ZoneSettings<%s>' % self.zone.name


class Record(object):
    _data = ()
    _own_attrs = ('zone', '_service', '_data', '_saved_data')

    def __init__(self, zone, data):
        self.zone = zone
        self._service = zone._service
        self._set_data(data)

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError()

    def __setattr__(self, name, value):
        if name in self._own_attrs:
            return super(Record, self).__setattr__(name, value)
        if name in self._data:
            self._data[name] = value
        else:
            raise AttributeError()

    def _set_data(self, data):
        self._saved_data = data
        self._data = deepcopy(data)

    def save(self):
        if self._saved_data != self._data:
            result = self._service.update_dns_record(self.zone.id, self.id,
                                                     self._data)
            if self._data['name'] != self._saved_data['name']:
                clear_property_cache(self.zone, 'records')
            self._set_data(result)

    def delete(self):
        self._service.delete_dns_record(self.zone.id, self.id)
        clear_property_cache(self.zone, 'records')

    def __repr__(self):
        return 'Record<%s %s IN %s %s>' % (self.name, self.ttl, self.type,
                                           self.content)
