#!/usr/bin/env python

import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

config = {
    'description': 'Prometheus Utils',
    'long_description': README,
    'url': 'git@github.com:yulinzou-wish/prometheus-utils.git',
    'author': 'chn-infra',
    'author_email': 'chn-infra@wish.com',
    'license': 'MIT',
    'platforms': 'any',
    'classifiers': [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    'version': 'wish_0.1',
    'packages': find_packages(),
    'package_data': {'prometheus_utils': ['prometheus_client/*']},
    'scripts': [],
    'name': 'prometheus_utils',
}

setup(**config)
