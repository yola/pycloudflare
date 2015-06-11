from itertools import count

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
        super(CloudFlareService, self).__init__(config['url'], headers=headers)

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
