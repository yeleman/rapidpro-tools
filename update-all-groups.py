#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from rapidpro_tools import logger
from rapidpro_tools.mongo import contacts
from rapidpro_mali import update_groups


def main():
    uuids = [c['uuid'] for c in contacts.find({})]
    logger.info(len(uuids))
    for uuid in uuids:
        logger.info(uuid)
        update_groups(contacts.find_one({'uuid': uuid}), remove_others=True)

if __name__ == '__main__':
    main()
