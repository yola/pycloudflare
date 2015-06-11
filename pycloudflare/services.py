from itertools import count
from urllib import urlencode

from demands import HTTPServiceClient
from yoconfig import get_config


class CloudFlareService(HTTPServiceClient):
    def __init__(self, **kwargs):
        config = get_config('cloudflare')
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Key': config['api_key'],
            'X-Auth-Email': config['email']
        }
        self._organization = config.get('organization')
        super(CloudFlareService, self).__init__(
            config['url'], headers=headers, send_as_json=True)

    def iter_zones(self):
        for page in count():
            batch = self.get(
                'zones?page=%i&per_page=50' % page).json()['result']
            if not batch:
                return
            for result in batch:
                yield result

    def get_zones(self):
        return list(self.iter_zones())

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id).json()['result']

    def get_zone_by_name(self, name):
        url = 'zones?' + urlencode({'name': name})
        result = self.get(url).json()['result']
        assert len(result) <= 1
        return result[0]

    def create_zone(self, name, jump_start=False):
        data = {
            'name': name,
            'jump_start': jump_start,
        }
        if self._organization:
            data['organization'] = {'id': self._organization}
        return self.post('zones', data).json()['result']

    def delete_zone(self, zone_id):
        return self.delete('zones/%s' % zone_id)
