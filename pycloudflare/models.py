from property_caching import cached_property, clear_property_cache

from pycloudflare.services import CloudFlareHostService, CloudFlareService


class User(object):
    _host_service = None

    def __init__(self, email, api_key, host_api_data=None):
        self.api_key = api_key
        self.email = email
        self._host_api_data = host_api_data
        self.service = self.get_service(email, api_key)

    def __getattr__(self, name):
        if name in ('user_key', 'unique_id'):
            if not self._host_api_data:
                service = self.get_host_service()
                self._host_api_data = service.user_lookup(email=self.email)
            return self._host_api_data[name]
        raise AttributeError()

    @classmethod
    def get_host_service(cls):
        if cls._host_service is None:
            cls._host_service = CloudFlareHostService()
        return cls._host_service

    @classmethod
    def get_service(cls, email, api_key):
        return CloudFlareService(email=email, api_key=api_key)

    @classmethod
    def get_or_create(cls, email, password, username=None, unique_id=None):
        service = cls.get_host_service()
        data = service.user_create(email=email, password=password,
                                   username=username, unique_id=unique_id)
        api_key = data.pop('user_api_key')
        email = data.pop('cloudflare_email')
        return User(email, api_key, host_api_data=data)

    @classmethod
    def get(cls, email=None, unique_id=None):
        service = cls.get_host_service()
        data = service.user_lookup(email=email, unique_id=unique_id)
        api_key = data.pop('user_api_key')
        email = data.pop('cloudflare_email')
        return User(email, api_key, host_api_data=data)

    @cached_property
    def zones(self):
        return list(self.iter_zones())

    def iter_zones(self):
        for zone in self.service.iter_zones():
            yield Zone(self, zone)

    def get_zone_by_name(self, name):
        zone = self.service.get_zone_by_name(name)
        return Zone(self, zone)

    def create_zone(self, name, jump_start=False):
        zone = self.service.create_zone(name=name, jump_start=jump_start)
        return Zone(self, zone)

    def __repr__(self):
        return 'User<%s>' % self.email


class Zone(object):
    def __init__(self, user, data):
        self.user = user
        self.service = user.service
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError()

    def delete(self):
        self.service.delete_zone(self.id)
        clear_property_cache(self.user, 'zones')

    @cached_property
    def settings(self):
        return ZoneSettings(self)

    def iter_records(self):
        for record in self.service.iter_dns_records(self.id):
            yield Record(self, record)

    @cached_property
    def records(self):
        by_name = {}
        for record in self.iter_records():
            by_name.setdefault(record.name, [])
            by_name[record.name].append(record)
        return by_name

    def create_record(self, name, type, content, ttl=1, proxied=False,
                      **kwargs):
        data = {
            'name': name,
            'type': type,
            'content': content,
            'ttl': ttl,
            'proxied': proxied,
        }
        if type == 'MX':
            data['priority'] = kwargs.pop('priority')
        assert kwargs == {}

        record = self.service.create_dns_record(self.id, data)
        clear_property_cache(self, 'records')
        return Record(self, record)

    def __repr__(self):
        return 'Zone<%s>' % self.name


class ZoneSettings(object):
    def __init__(self, zone):
        self.zone = zone
        self.service = zone.service
        self._settings = self.service.get_zone_settings(self.zone.id)
        self._updates = {}

    def __getattr__(self, name):
        if name in self._updates:
            return self._updates[name]
        if name in self._settings:
            return self._settings[name]['value']
        raise AttributeError()

    def __setattr__(self, name, value):
        if name in ('zone', 'service', '_settings', '_updates'):
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
                 for name, value in self._updates.iteritems()]
        self.service.set_zone_settings(self.zone.id, items)
        self._settings = self.service.get_zone_settings(self.zone.id)
        self._updates = {}

    def __iter__(self):
        return iter(sorted(self._settings))

    def __repr__(self):
        return 'ZoneSettings<%s>' % self.zone.name


class Record(object):
    _data = ()

    def __init__(self, zone, data):
        self.zone = zone
        self.service = zone.service
        self._data = data
        self._updates = {}

    def __getattr__(self, name):
        if name in self._updates:
            return self._updates[name]
        if name in self._data:
            return self._data[name]
        raise AttributeError()

    def __setattr__(self, name, value):
        if name in ('zone', 'service', '_data', '_updates'):
            return super(Record, self).__setattr__(name, value)
        if name in self._data:
            self._updates[name] = value
        else:
            raise AttributeError()

    def save(self):
        if self._updates:
            r = self.service.update_dns_record(self.zone.id, self.id,
                                               self._updates)
            self._data.update(r)
            if 'name' in self._updates:
                clear_property_cache(self.zone, 'records')
            self._updates = {}

    def delete(self):
        self.service.delete_dns_record(self.zone.id, self.id)
        clear_property_cache(self.zone, 'records')

    def __repr__(self):
        return 'Record<%s %s IN %s %s>' % (self.name, self.ttl, self.type,
                                           self.content)
