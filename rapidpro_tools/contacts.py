#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2

from rapidpro_tools import logger
from rapidpro_tools.mongo import contacts
from rapidpro_tools.utils import post_api_data, phone_to_name

if PY2:
    import unicodecsv as csv
else:
    import csv

NAME_OK_FIELD = '_name_is_ok'
CSV_HEADERS = ['uuid', 'is_ok', 'name']


def update_contact(contact, fields=None, name=None, groups=None):

    update_dict = {'urns': contact['urns']}

    if name is not None:
        update_dict.update({'name': name})

    if fields is not None:
        update_dict.update({'fields': fields})

    if groups is not None:
        update_dict.update({'groups': groups})

    if len(update_dict.keys()) <= 1:
        # nothing to update
        return False

    # upload edits
    contact.update(post_api_data('/contacts.json', update_dict))

    # save returned (updated) contacts details in DB
    contacts.save(contact)

    return contact


def export_contact_names_to(afile):
    csv_writer = csv.DictWriter(afile, CSV_HEADERS)
    csv_writer.writeheader()

    query = {NAME_OK_FIELD: {'$exists': False}}
    for contact in contacts.find(query, {'uuid': True, 'name': True}):
        csv_writer.writerow({
            'uuid': contact.get('uuid'),
            'name': contact.get('name') or "",
            'is_ok': contact.get(NAME_OK_FIELD) or ""
        })


def fix_contact_names_from(afile):
    csv_reader = csv.DictReader(afile, CSV_HEADERS)

    for entry in csv_reader:
        if csv_reader.line_num == 1:
            continue

        if not entry.get('is_ok') or not entry.get('uuid'):
            continue

        uuid = entry.get('uuid').strip()

        name = entry.get('name').strip() or ""

        contact = contacts.find_one({'uuid': uuid})

        # rapidpro doesn't update contact if name is empty
        if not name:
            name = phone_to_name(contact.get('phone'))

        if contact['name'] != name:
            logger.info("Updating {}: {}".format(uuid, name))

            update_contact(contact=contact, name=name)
