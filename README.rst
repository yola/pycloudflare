pycloudflare
============


|Build Status|

A Python client for CloudFlare

Usage
-----

Get all our zones at CloudFlare

.. code:: python

    >>> cf = CloudFlareService()
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
