#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

# from rapidpro_tools import logger
from rapidpro_tools.mongo import contacts
from rapidpro_tools.utils import post_api_data


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
