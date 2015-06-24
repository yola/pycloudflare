import logging
from urllib import urlencode

from demands import HTTPServiceClient, HTTPServiceError
from yoconfig import get_config

from pycloudflare.pagination import PaginatedAPIIterator

log = logging.getLogger(__name__)


class CloudFlarePageIterator(PaginatedAPIIterator):
    page_size_param = 'per_page'
    page_size = 50


class CloudFlareService(HTTPServiceClient):
    def __init__(self, api_key, email):
        config = get_config('cloudflare')
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Key': api_key,
            'X-Auth-Email': email,
        }
        url = config['url'] + 'client/v4/'
        super(CloudFlareService, self).__init__(
            url, headers=headers, send_as_json=True)

    def post_send(self, response, **kwargs):
        response = super(CloudFlareService, self).post_send(response, **kwargs)
        return response.json()['result']

    def _get_paginated(self, base_url, page, per_page):
        params = {
            'page': page,
            'per_page': per_page,
        }
        return self.get(base_url + '?' + urlencode(params))

    def get_zones(self, page=0, per_page=CloudFlarePageIterator.page_size):
        return self._get_paginated('zones', page, per_page)

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id)

    def get_zone_by_name(self, name):
        result = self.get('zones?' + urlencode({'name': name}))
        assert len(result) <= 1
        return result[0]

    def get_zone_settings(self, zone_id, page=0,
                          per_page=CloudFlarePageIterator.page_size):
        url = 'zones/%s/settings' % zone_id
        return self._get_paginated(url, page, per_page)

    def set_zone_settings(self, zone_id, items):
        data = {'items': items}
        return self.patch('zones/%s/settings' % zone_id, data)

    def get_zone_setting(self, zone_id, setting):
        return self.get('zones/%s/settings/%s' % (zone_id, setting))

    def set_zone_setting(self, zone_id, setting, value):
        url = 'zones/%s/settings/%s' % (zone_id, setting)
        return self.patch(url, {'value': value})

    def create_zone(self, name, jump_start=False, organization=None):
        data = {
            'name': name,
            'jump_start': jump_start,
        }
        if organization:
            data['organization'] = {'id': self._organization}
        return self.post('zones', data)

    def delete_zone(self, zone_id):
        return self.delete('zones/%s' % zone_id)

    def get_dns_records(self, zone_id, page=0,
                        per_page=CloudFlarePageIterator.page_size):
        url = 'zones/%s/dns_records' % zone_id
        return self._get_paginated(url, page, per_page)

    def get_dns_record(self, zone_id, record_id):
        return self.get('zones/%s/dns_records/%s' % (zone_id, record_id))

    def create_dns_record(self, zone_id, content):
        return self.post('zones/%s/dns_records' % zone_id, content)

    def update_dns_record(self, zone_id, record_id, content):
        url = 'zones/%s/dns_records/%s' % (zone_id, record_id)
        return self.patch(url, content)

    def delete_dns_record(self, zone_id, record_id):
        return self.delete('zones/%s/dns_records/%s' % (zone_id, record_id))


class CloudFlareHostPageIterator(PaginatedAPIIterator):
    page_param = 'offset'
    page_size_param = 'limit'
    page_size = 100
    pagination_type = 'item'


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
        response_json = response.json()
        if response_json['result'] == 'error':
            err_code = response_json['err_code']
            msg = response_json['msg']
            data = kwargs['data'].copy()
            data.pop('host_key')
            act = data.pop('act')
            log.error('Error response %s: %s from %s with %r',
                      err_code, msg, act, data)
            raise HTTPServiceError(response)
        return response_json['response']

    def user_create(self, email, password, username=None, unique_id=None):
        data = {
            'act': 'user_create',
            'cloudflare_email': email,
            'cloudflare_pass': password,
            'cloudflare_username': username,
            'unique_id': unique_id,
        }
        return self.post(self.gw, data)

    def user_lookup(self, email=None, unique_id=None):
        if not (email or unique_id):
            raise ValueError('Requires email or unique_id')
        data = {
            'act': 'user_lookup',
            'cloudflare_email': email,
            'unique_id': unique_id,
        }
        return self.post(self.gw, data)

    def zone_list(self, zone_name=None, zone_status=None, sub_id=None,
                  sub_status=None, offset=0,
                  limit=CloudFlareHostPageIterator.page_size):
        data = {
            'act': 'zone_list',
            'limit': limit,
            'sub_id': sub_id,
            'sub_status': sub_status,
            'zone_name': zone_name,
            'zone_status': zone_status,
        }
        return self.post(self.gw, data)
