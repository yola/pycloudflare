#!/usr/bin/env python
from setuptools import setup
import pycloudflare


setup(
    name=pycloudflare.__name__,
    version=pycloudflare.__version__,
    description=pycloudflare.__doc__,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=pycloudflare.__url__,
    packages=['pycloudflare'],
    test_suite='nose.collector',
    install_requires=[
        'demands >= 1.0.5, < 2.0.0',
        'property-caching >= 1.0.0, < 2.0.0',
    ]
)
