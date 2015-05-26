pycloudflare
============

A Python client for CloudFlare

## Usage

Get all our zones at CloudFlare

```python
>>> cf = CloudFlareService()
>>> for domain in cf.get_zones():
>>>     print domain['name'], domain['id']
```

## Configuration

The service client is configured when it is instantiated and reads its
configuration from `yoconfig`:

Django (or other) applications wishing to configure the service client,
can use `yoconfig.configure_services`.

```python
from yoconfig import configure_services

configure_services('application_name', ['cloudflare'], {
    'cloudflare': {
        'url': 'https://api.cloudflare.com/client/v4/',
        'api_key': '<api_key>',
        'email': 'tech@yola.com'
    },
})
```

## Testing

Install development requirements:

    pip install -r requirements.txt

Tests can then be run by doing:

    nosetests
