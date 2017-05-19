pycloudflare
============


|Build Status|

A Python client for CloudFlare API v4 and Host API.

It provides two levels of integration against the CloudFlare API:

#. A low level API, with one method per API endpoint
   (``pycloudflare.services``).
#. A high level ORM API (``pycloudflare.models``).

Only a subset of the CloudFlare API is currently supported:

* Users
* Zones
* Zone Settings
* DNS Records
* Page Rules
* User creation & authentication through CloudFlare's partner-facing
  Host API.

Usage
-----

Get all our zones at CloudFlare

.. code:: python

    >>> cf = CloudFlareService(api_key, email)
    >>> for domain in cf.get_zones():
    >>>     print domain['name'], domain['id']

Configuration
-------------

The Host (Partner) API service client is configured when it is
instantiated and reads its configuration from ``configuration.json``.

The configuration file should be in the format:

.. code:: json

    {
        "common": {
            "cloudflare": {
                "api_key": "HOST API KEY HERE",
             }
        }
    }

Testing
-------

Install development requirements::

    pip install -r requirements.txt

Tests can then be run by doing::

    nosetests

The integration tests require a host API key. They can be run with::

    nosetests tests/test_integration.py

.. |Build Status| image:: https://travis-ci.org/yola/pycloudflare.svg?branch=master
   :target: https://travis-ci.org/yola/pycloudflare
