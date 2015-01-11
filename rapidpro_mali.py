#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re

from rapidpro_tools.contacts import update_contact

MALITEL = 485
ORANGE = 417

BKO = "District de Bamako"
GAO = "Gao"
KAYES = "Kayes"
KKR = "Koulikoro"
MOPTI = "Mopti"
SEGOU = "Ségou"
SIKASSO = "Sikasso"
TBKT = "Tombouctou"
KIDAL = "Kidal"


def ucontact_states(contact):

    states_map = {
        'Bamako District': BKO,
        'KAYE': KAYES,
        'bamoko': BKO,
        'MOPTU': MOPTI,
        'Tombauctou': TBKT,
        'SEGOU SEGOU': SEGOU,
        'SIkasso SIkasso': SIKASSO,
        'Koulikoro Koulikoro Koulikoro': KKR,
        'Mopte': MOPTI,
        'Tomboctou Tomboctou': TBKT,
        'Toumbouctou': TBKT,
        'Tonbouctou': TBKT,
        'Toubouctou': TBKT,
        'Kaye': KAYES,
        'tambouctou': TBKT,
        'SIKASSO SIKASSO': SIKASSO,
        'Sikasso Sikasso': SIKASSO,
        'KOULIKORO KOULIKORO KOULIKORO': KKR,
        'bko': BKO,
        'Bko': BKO,
        'tomboctou tomboctou': TBKT,
        'BKO': BKO,
        'tonbouctou': TBKT,
        'Mopty': MOPTI,
        'bamko': BKO,
        'segou segou': SEGOU,
        'Segou Segou': SEGOU,
        'sikasso sikasso': SIKASSO,
        'Mopto': MOPTI,
        'TOMBOCTOU TOMBOCTOU': TBKT,
    }

    if not contact['fields']['state'] in states_map.keys():
        return False

    fields = {
        'state': states_map.get(contact['fields']['state'])
    }

    return update_contact(contact, fields=fields)


def relayer_from_number(num):
    if num[0] in ('7', '8'):
        return ORANGE
    if num[0] in ('9',) and num[1] in ('1', '2', '3', '4', '5'):
        return ORANGE

    if num[0] in ('6',):
        return MALITEL

    if num[0] in ('9',) and num[1] in ('6', '7', '8', '9'):
        return MALITEL

    return


def clean_number(num):
    # cleanup formating
    num = "".join(i for i in num if i.isdigit() or i == '+')

    if num.count('+') > 1:
        return

    # is intl format?
    if num.startswith('+'):
        num = re.sub(r'^\+223', '', num)

    # intl yet not Mali
    if num.count('+') > 0:
        return

    # not mali fmt
    if len(num) != 8:
        return

    # not a mali mobile number
    if num[0] not in ('6', '7', '8', '9'):
        return

    return num
