#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
from logging.config import dictConfig
import json
import sys

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'iso8601': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },
        'peewee': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },
        'requests': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

dictConfig(LOGGING)
logger = logging.getLogger(__name__)


def change_logging_level(debug=False):
    level = 'DEBUG' if debug else 'INFO'
    for logger in LOGGING['loggers'].keys():
        LOGGING['loggers'][logger]['level'] = level
    dictConfig(LOGGING)


try:
    CONFIG = json.load(open('config.json', 'r'))
    for key in ('api_token', 'server_url',
                'mongo_url', 'mongo_database',
                'relayers_unicode'):
        assert key in CONFIG.keys() and CONFIG.get(key) is not None
except AssertionError as e:
    logger.error("Missing value(s) in config file.")
    sys.exit(1)
except Exception as e:
    logger.error("No config file present. Exiting.")
    sys.exit(1)
