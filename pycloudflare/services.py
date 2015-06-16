import logging
from itertools import count
from urllib import urlencode

from demands import HTTPServiceClient, HTTPServiceError
from yoconfig import get_config


log = logging.getLogger(__name__)


class CloudFlareService(HTTPServiceClient):
    def __init__(self, api_key, email, organization=None):
        config = get_config('cloudflare')
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Key': api_key,
            'X-Auth-Email': email,
        }
        self._organization = organization
        url = config['url'] + 'client/v4/'
        super(CloudFlareService, self).__init__(
            url, headers=headers, send_as_json=True)

    def post_send(self, response, **kwargs):
        response = super(CloudFlareService, self).post_send(response, **kwargs)
        return response.json()['result']

    def _iter_pages(self, base_url, params=None, page_size=50):
        base_params = params or {}
        base_params['per_page'] = page_size

        for page in count():
            params = base_params.copy()
            params['page'] = page
            url = base_url + '?' + urlencode(params)
            batch = self.get(url)
            for result in batch:
                yield result
            if len(batch) < page_size:
                return

    def iter_zones(self):
        return self._iter_pages('zones')

    def get_zones(self):
        return list(self.iter_zones())

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id)

    def get_zone_by_name(self, name):
        result = self.get('zones?' + urlencode({'name': name}))
        assert len(result) <= 1
        return result[0]

    def iter_zone_settings(self, zone_id):
        for setting in self._iter_pages('zones/%s/settings' % zone_id):
            yield setting['id'], setting

    def get_zone_settings(self, zone_id):
        return dict(self.iter_zone_settings(zone_id))

    def get_zone_setting(self, zone_id, setting):
        return self.get('zones/%s/settings/%s' % (zone_id, setting))

    def set_zone_setting(self, zone_id, setting, value):
        url = 'zones/%s/settings/%s' % (zone_id, setting)
        return self.patch(url, {'value': value})

    def create_zone(self, name, jump_start=False):
        data = {
            'name': name,
            'jump_start': jump_start,
        }
        if self._organization:
            data['organization'] = {'id': self._organization}
        return self.post('zones', data)

    def delete_zone(self, zone_id):
        return self.delete('zones/%s' % zone_id)

    def iter_dns_records(self, zone_id):
        return self._iter_pages('zones/%s/dns_records' % zone_id)

    def get_dns_records(self, zone_id):
        return list(self.iter_dns_records(zone_id))

    def get_dns_record(self, zone_id, record_id):
        return self.get('zones/%s/dns_records/%s' % (zone_id, record_id))

    def create_dns_record(self, zone_id, content):
        return self.post('zones/%s/dns_records' % zone_id, content)

    def update_dns_record(self, zone_id, record_id, content):
        url = 'zones/%s/dns_records/%s' % (zone_id, record_id)
        return self.patch(url, content)

    def delete_dns_record(self, zone_id, record_id):
        return self.delete('zones/%s/dns_records/%s' % (zone_id, record_id))


class CloudFlareHostService(HTTPServiceClient):
    def __init__(self, **kwargs):
        config = get_config('cloudflare')
        data = {
            'host_key': config['api_key'],
        }
        self.gw = 'host-gw.html'
        super(CloudFlareHostService, self).__init__(config['url'], data=data)

    def post_send(self, response, **kwargs):
        """
        These endpoints don't use HTTP response codes to indicate
        application-level errors
        """
        response = super(CloudFlareHostService, self).post_send(
            response, **kwargs)
        if response.json()['result'] == 'error':
            err_code = response.json()['err_code']
            msg = response.json()['msg']
            data = kwargs['data'].copy()
            data.pop('host_key')
            act = data.pop('act')
            log.error('Error response %s: %s from %s with %r',
                      err_code, msg, act, data)
            raise HTTPServiceError(response)
        return response.json()['response']

    def user_create(self, email, password, username=None, unique_id=None):
        data = {
            'act': 'user_create',
            'cloudflare_email': email,
            'cloudflare_pass': password,
        }
        if username:
            data['cloudflare_username'] = username
        if unique_id:
            data['unique_id'] = unique_id
        return self.post(self.gw, data)

    def user_lookup(self, email=None, unique_id=None):
        data = {
            'act': 'user_lookup',
        }
        if email:
            data['cloudflare_email'] = email
        elif unique_id:
            data['unique_id'] = unique_id
        else:
            raise ValueError('Requires email or unique_id')
        return self.post(self.gw, data)

    def iter_zone_list(self, zone_name=None, zone_status=None, sub_id=None,
                       sub_status=None):
        limit = 100
        data = {
            'act': 'zone_list',
            'limit': limit,
        }
        if zone_name:
            data['zone_name'] = zone_name
        if zone_status:
            data['zone_status'] = zone_status
        if sub_id:
            data['sub_id'] = sub_id
        if sub_status:
            data['sub_status'] = sub_status
        for offset in count(0, limit):
            data['offset'] = offset
            zones = self.post(self.gw, data)
            for zone in zones:
                yield zone
            if len(zones) < limit:
                break
