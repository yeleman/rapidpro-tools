#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re
import datetime
from itertools import combinations

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

PROFILE_FIELDS = [
    "Date de naissance",  # U-Reporter Jeunes / U-Reporer Adultes
    "Sexe",  # U-Reporer Hommes / U-Reporter Femmes
    "Region",  # District de Bamako, Gao, Kayes, Koulikoro, Mopti,
               # Ségou, Sikasso, Tombouctou, Kidal
    "Milieu",  # Ville / Village
    "Activite",  # Etudiant / Travaille / Sans Activité
]

groups = {
    "Age: Moins de 20 ans":
        lambda c: int(c["fields"]["born"]) >=
        (datetime.datetime.today().year - 20),
    "Age: 20-30 ans":
        lambda c: int(c["fields"]["born"]) in range(
            datetime.datetime.today().year - 30,
            datetime.datetime.today().year - 20),
    "Age: 30-40 ans":
        lambda c: int(c["fields"]["born"]) in range(
            datetime.datetime.today().year - 40,
            datetime.datetime.today().year - 30),
    "Age: 40-50 ans":
        lambda c: int(c["fields"]["born"]) in range(
            datetime.datetime.today().year - 50,
            datetime.datetime.today().year - 40),
    "Age: n/a":
        lambda c: not c["fields"]["born"].isdigit(),

    "Sexe: Hommes": lambda c: c["fields"]["gender"] == "Homme",
    "Sexe: Femmes": lambda c: c["fields"]["gender"] == "Femme",
    "Sexe: n/a": lambda c: c["fields"]["gender"] not in ("Homme", "Femme"),

    "Milieu: Village": lambda c: c["fields"]["milieu"] == "Village",
    "Milieu: Ville": lambda c: c["fields"]["milieu"] == "Ville",
    "Milieu: n/a": lambda c: c["fields"]["milieu"] not in ("Ville", "Village"),

    "Activité: Étudiant": lambda c: c["fields"]["activit"] == "Etudiant",
    "Activité: Travaille": lambda c: c["fields"]["activit"] == "Travaille",
    "Activité: Sans activité":
        lambda c: c["fields"]["activit"] == "Sans Activité",
    "Activité: n/a":
        lambda c: c["fields"]["activit"] not in (
            "Etudiant", "Travaille", "Sans Activité"),
    "Région: Bamako": lambda c: c["fields"]["state"] == "District de Bamako",
    "Région: Gao": lambda c: c["fields"]["state"] == "Gao",
    "Région: Kayes": lambda c: c["fields"]["state"] == "Kayes",
    "Région: Koulikoro": lambda c: c["fields"]["state"] == "Koulikoro",
    "Région: Mopti": lambda c: c["fields"]["state"] == "Mopti",
    "Région: Ségou": lambda c: c["fields"]["state"] == "Ségou",
    "Région: Sikasso": lambda c: c["fields"]["state"] == "Sikasso",
    "Région: Tombouctou": lambda c: c["fields"]["state"] == "Tombouctou",
    "Région: Kidal": lambda c: c["fields"]["state"] == "Kidal",
    "Région: n/a": lambda c: c["fields"]["state"] not in (
        "District de Bamako", "Gao", "Kayes", "Koulikoro", "Mopti",
        "Ségou", "Sikasso", "Tombouctou", "Kidal")
}


def match_group(contact, group_name):
    try:
        return groups.get(group_name)(contact)
    except:
        return False


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
    if num[0] in ('9',) and num[1] in ('0', '1', '2', '3', '4'):
        return ORANGE

    if num[0] in ('6',):
        return MALITEL

    if num[0] in ('9',) and num[1] in ('5', '6', '7', '8', '9'):
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


def update_groups(contact, remove_others=False):
    if remove_others:
        cgroups = []
    else:
        cgroups = contact['groups']

    # default group for all with a registration date (started reg flow)
    default_group = "U-Reporters"
    if contact['fields'].get('registration_date', None):
        if default_group not in cgroups:
            cgroups.append(default_group)
    else:
        if default_group in cgroups:
            cgroups.remove(default_group)

    # cartesian product ** (no duplicate combination) of all groups
    all_groups = combinations(groups.keys(), 2)

    def handle_group(group_name, force_match=False):
        if force_match or match_group(contact=contact, group_name=group_name):
            if group_name in cgroups:
                pass
            else:
                cgroups.append(group_name)
            return True
        else:
            if group_name in cgroups:
                cgroups.remove(group_name)
            return False

    for groupa_name, groupb_name in all_groups:
        if handle_group(groupa_name) and handle_group(groupb_name):
            groupc_name = "{} - {}".format(groupa_name, groupb_name)
            handle_group(groupc_name, force_match=True)

    update_contact(contact=contact, groups=cgroups)
