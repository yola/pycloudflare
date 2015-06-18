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
    _settings = ()

    def __init__(self, zone):
        self.zone = zone
        self.service = zone.service

    def __getitem__(self, name):
        self.get_settings()
        if name in self._settings:
            return self._settings[name]['value']
        raise KeyError()

    def __setitem__(self, name, value):
        self.service.set_zone_setting(self.zone.id, name, value)
        if self._settings:
            self._settings[name]['value'] = value

    def __iter__(self):
        self.get_settings()
        return iter(sorted(self._settings))

    def get_settings(self):
        if not self._settings:
            self._settings = self.service.get_zone_settings(self.zone.id)

    def __repr__(self):
        return 'ZoneSettings<%s>' % self.zone.name


class Record(object):
    _data = ()

    def __init__(self, zone, data):
        self.zone = zone
        self.service = zone.service
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError()

    def __setattr__(self, name, value):
        if name not in self._data:
            return super(Record, self).__setattr__(name, value)
        data = {name: value}
        r = self.service.update_dns_record(self.zone.id, self.id, data)
        self._data.update(r)
        if name == 'name':
            clear_property_cache(self.zone, 'records')

    def delete(self):
        self.service.delete_dns_record(self.zone.id, self.id)
        clear_property_cache(self.zone, 'records')

    def __repr__(self):
        return 'Record<%s %s IN %s %s>' % (self.name, self.ttl, self.type,
                                           self.content)
