from demands import HTTPServiceClient, HTTPServiceError
from demands.pagination import (
    PAGE_PARAM, PAGE_SIZE_PARAM, PAGE_SIZE, PAGINATION_TYPE, RESULTS_KEY,
    PaginatedResults, PaginationType)
from six.moves.urllib.parse import urlencode

from pycloudflare.config import get_config
from pycloudflare.exceptions import AccountNotFound, CustomHostnameNotFound


class ZoneNotFound(Exception):
    pass


CF_PAGINATION_OPTIONS = {
    PAGE_SIZE_PARAM: 'per_page',
    PAGE_SIZE: 50,
    RESULTS_KEY: None,
}
_ADMINSTRATOR_ROLE_ID = '05784afa30c1afe1440e79d9351c7430'


def cloudflare_paginated_results(fn, args=(), kwargs=None):
    return PaginatedResults(fn, args=args, kwargs=kwargs,
                            **CF_PAGINATION_OPTIONS)


class CloudFlareService(HTTPServiceClient):

    def __init__(self, api_key, email):
        headers = {
            'X-Auth-Key': api_key,
            'X-Auth-Email': email,
        }
        url = 'https://api.cloudflare.com/client/v4/'
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

    def create_account(self, name, account_type='standard'):
        return self.post('accounts', json={
            'name': name,
            'type': account_type
        })

    def get_account_by_name(self, name):
        result = self.get('accounts', params={'name': name})
        assert len(result) <= 1
        if not result:
            raise AccountNotFound()

        return result[0]

    def add_account_member(
            self, account_id, email, role=_ADMINSTRATOR_ROLE_ID):
        return self.post('accounts/{}/members'.format(account_id), json={
            'email': email,
            'roles': [role]
        })

    def list_account_members(self, account_id, page=1, per_page=20):
        return self._get_paginated(
            'accounts/{}/members'.format(account_id), page, per_page)

    def delete_account_member(self, account_id, member_id):
        return self.delete(
            'accounts/{}/members/{}'.format(account_id, member_id))

    def get_zones(self, page=1, per_page=CF_PAGINATION_OPTIONS[PAGE_SIZE]):
        return self._get_paginated('zones', page, per_page)

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id)

    def get_zone_by_name(self, name):
        result = self.get('zones?' + urlencode({'name': name}))
        assert len(result) <= 1
        if not result:
            raise ZoneNotFound()

        return result[0]

    def get_zone_settings(self, zone_id):
        return self.get('zones/%s/settings' % zone_id)

    def set_zone_settings(self, zone_id, items):
        data = {'items': items}
        return self.patch('zones/%s/settings' % zone_id, json=data)

    def get_zone_setting(self, zone_id, setting):
        return self.get('zones/%s/settings/%s' % (zone_id, setting))

    def set_zone_setting(self, zone_id, setting, value):
        url = 'zones/%s/settings/%s' % (zone_id, setting)
        return self.patch(url, json={'value': value})

    def create_zone(self, name, account_id):
        return self.post('zones', json={
            'name': name,
            'account': {'id': account_id}
        })

    def delete_zone(self, zone_id):
        return self.delete('zones/%s' % zone_id)

    def get_dns_records(self, zone_id, page=1,
                        per_page=CF_PAGINATION_OPTIONS[PAGE_SIZE]):
        url = 'zones/%s/dns_records' % zone_id
        return self._get_paginated(url, page, per_page)

    def get_dns_record(self, zone_id, record_id):
        return self.get('zones/%s/dns_records/%s' % (zone_id, record_id))

    def create_dns_record(self, zone_id, content):
        return self.post('zones/%s/dns_records' % zone_id, json=content)

    def update_dns_record(self, zone_id, record_id, content):
        url = 'zones/%s/dns_records/%s' % (zone_id, record_id)
        return self.patch(url, json=content)

    def delete_dns_record(self, zone_id, record_id):
        return self.delete('zones/%s/dns_records/%s' % (zone_id, record_id))

    def get_page_rules(self, zone_id, page=1,
                       per_page=CF_PAGINATION_OPTIONS[PAGE_SIZE]):
        url = 'zones/%s/pagerules' % zone_id
        return self._get_paginated(url, page, per_page)

    def get_page_rule(self, zone_id, rule_id):
        return self.get('zones/%s/pagerules/%s' % (zone_id, rule_id))

    def create_page_rule(self, zone_id, content):
        return self.post('zones/%s/pagerules' % zone_id, json=content)

    def update_page_rule(self, zone_id, rule_id, content):
        url = 'zones/%s/pagerules/%s' % (zone_id, rule_id)
        return self.patch(url, json=content)

    def delete_page_rule(self, zone_id, rule_id):
        return self.delete('zones/%s/pagerules/%s' % (zone_id, rule_id))

    def purge_cache(self, zone_id, files=None, tags=None, hosts=None):
        data = {}
        if files:
            data['files'] = files
        if tags:
            data['tags'] = tags
        if hosts:
            data['hosts'] = hosts

        if not data:
            data['purge_everything'] = True

        return self.delete('zones/%s/purge_cache' % zone_id, json=data)

    def get_ssl_universal_settings(self, zone_id):
        return self.get('zones/%s/ssl/universal/settings' % zone_id)

    def update_ssl_universal_settings(self, zone_id, content):
        return self.patch(
            'zones/%s/ssl/universal/settings' % zone_id, json=content)

    def get_ssl_verification_info(self, zone_id):
        return self.get('zones/%s/ssl/verification' % zone_id)

    def create_custom_hostname(self, zone_id, hostname, ssl_settings):
        data = {
            'hostname': hostname,
            'ssl': ssl_settings
        }
        return self.post(
            'zones/{}/custom_hostnames'.format(zone_id), json=data)

    def get_custom_hostname_by_name(self, zone_id, hostname):
        result = self.get(
            'zones/{}/custom_hostnames'.format(zone_id),
            params={'hostname': hostname})

        if not result:
            raise CustomHostnameNotFound()

        return result[0]

    def update_custom_hostname(self, zone_id, hostname_id, **data):
        return self.patch(
            'zones/{}/custom_hostnames/{}'.format(zone_id, hostname_id),
            json=data)

    def delete_custom_hostname(self, zone_id, hostname_id):
        return self.delete(
            'zones/{}/custom_hostnames/{}'.format(zone_id, hostname_id))


CF_HOST_PAGINATION_OPTIONS = {
    PAGE_PARAM: 'offset',
    PAGE_SIZE_PARAM: 'limit',
    PAGE_SIZE: 100,
    PAGINATION_TYPE: PaginationType.ITEM,
    RESULTS_KEY: None,
}


def cloudflare_host_paginated_results(fn, args=(), kwargs=None):
    return PaginatedResults(fn, args=args, kwargs=kwargs,
                            **CF_HOST_PAGINATION_OPTIONS)


class CloudFlareHostService(HTTPServiceClient):
    def __init__(self, **kwargs):
        config = get_config()
        data = {
            'host_key': config['api_key'],
        }
        url = 'https://api.cloudflare.com/'
        self.gw = 'host-gw.html'
        super(CloudFlareHostService, self).__init__(url, data=data)

    def post_send(self, response, **kwargs):
        """
        These endpoints don't use HTTP response codes to indicate
        application-level errors
        """
        response = super(CloudFlareHostService, self).post_send(
            response, **kwargs)
        response_json = response.json()
        if response_json['result'] == 'error':
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

    def full_zone_set(self, zone_name, user_key, jumpstart=False):
        data = {
            'act': 'full_zone_set',
            'jumpstart': int(jumpstart),
            'user_key': user_key,
            'zone_name': zone_name,
        }
        return self.post(self.gw, data)

    def zone_set(self, zone_name, user_key, subdomains, resolve_to):
        data = {
            'act': 'zone_set',
            'user_key': user_key,
            'zone_name': zone_name,
            'subdomains': ','.join(subdomains),
            'resolve_to': resolve_to,
        }
        return self.post(self.gw, data)

    def zone_list(self, zone_name=None, zone_status=None, sub_id=None,
                  sub_status=None, offset=0,
                  limit=CF_HOST_PAGINATION_OPTIONS[PAGE_SIZE]):
        data = {
            'act': 'zone_list',
            'limit': limit,
            'sub_id': sub_id,
            'sub_status': sub_status,
            'zone_name': zone_name,
            'zone_status': zone_status,
        }
        return self.post(self.gw, data)
