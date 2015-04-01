#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from pymongo import MongoClient

from rapidpro_tools import CONFIG

client = MongoClient(CONFIG.get('mongo_url'))
db = client[CONFIG.get('mongo_database')]

meta = db['meta']
contacts = db['contacts']
relayers = db['relayers']
messages = db['messages']
flows = db['flows']
runs = db['runs']
fields = db['fields']
