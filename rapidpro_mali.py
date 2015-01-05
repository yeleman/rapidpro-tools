#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from rapidpro_tools.contacts import update_contact

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
