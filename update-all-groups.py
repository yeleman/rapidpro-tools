#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from rapidpro_tools.mongo import contacts
from rapidpro_mali import update_groups


def main():
    print(contacts.find().count())
    for contact in contacts.find({}):
        update_groups(contact, remove_others=True)

if __name__ == '__main__':
    main()
