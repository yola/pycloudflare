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

    def get_zones(self):
        zones = []
        page = 1
        while True:
            batch = self.get(
                'zones?page=%s&per_page=50' % page).json()['result']
            if batch:
                zones.extend(batch)
            else:
                break
            page += 1
        return zones

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id).json()['result']
