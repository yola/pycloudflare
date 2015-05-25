from demands import HTTPServiceClient, HTTPServiceError
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
        return self.get('zones').json()['result']

    def get_zone(self, zone_id):
        return self.get('zones/%s' % zone_id).json()['result']
