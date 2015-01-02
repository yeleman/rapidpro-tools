#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import json
from collections import OrderedDict
import locale

from py3compat import text_type
from docopt import docopt
from jinja2 import Environment, FileSystemLoader

from rapidpro_tools import logger, change_logging_level
from rapidpro_tools.utils import tssort, datetime_from_iso

locale.setlocale(locale.LC_ALL, '')
jinja_env = Environment(loader=FileSystemLoader('.'))

help = ("""Usage: generate-dashboard.py -j FOLDER [-o FILE] [-v] [-h]

-h --help                       Display this help message
-v --verbose                    Display DEBUG messages
-j --json=<folder>              Path to JSON directory
-o --output=<path>              File path where to write HTML output"""
        """ (defaults to dashboard.html)

This script generates a custom static HTML Dashboard """
        """from usms-dashboard JSON. """)


def price_for_orange(month_data):
    total_in = month_data['stats']['nb_sms_in'][text_type(ORANGE)]
    total_out = month_data['stats']['nb_sms_out'][text_type(ORANGE)]
    mo_price = 25
    mt_price = 17
    ratio = 1.1
    nb_paying_out = total_out - total_in * ratio
    if nb_paying_out < 0:
        nb_paying_out = 0
    return mo_price * total_in + nb_paying_out * mt_price


def price_for_malitel(month_data):
    # Malitel are unique price 20F/sms in&out
    nb_total = month_data['stats']['nb_sms_total'][text_type(MALITEL)]
    price = 20 if nb_total <= 30000 else 15
    return nb_total * price


def price_for_others(month_data):
    return 50

ORANGE = 417
MALITEL = 485

RELAYERS = {
    ORANGE: ("orange", price_for_orange),
    MALITEL: ("malitel", price_for_malitel)
}


def percent(pc_value):
    return "{:.0f}%".format(pc_value * 100)


def number_format(value, precision=2):
    try:
        format = '%d'
        value = int(value)
    except:
        try:
            format = '%.' + '%df' % precision
            value = float(value)
        except:
            format = '%s'
        else:
            if value.is_integer():
                format = '%d'
                value = int(value)
    try:
        return locale.format(format, value, grouping=True)
    except Exception:
        pass
    return value


def relayer_css(relayer_id):
    return RELAYERS.get(int(relayer_id), ("others", None))[0]

jinja_env.filters['percent'] = percent
jinja_env.filters['amount'] = number_format
jinja_env.filters['relayer_css'] = relayer_css


def estimated_price_for(month_data, relayers):

    # init
    d = {'percent': {}, 'total': 0}

    # get raw prices for each operator
    for relayer_id, relayer in relayers.items():
        f = RELAYERS.get(relayer['relayer'], ("others", price_for_others))[1]
        d.update({relayer_id: f(month_data)})

    # update total amount
    d['total'] = sum([v for k, v in d.items()
                      if k not in ('percent', 'total')])

    # update percentages based on calculated values
    for relayer_id, relayer in relayers.items():
        pc = d[relayer_id] / d['total']
        d['percent'].update({relayer_id: pc})

    return d


def multiply_items(data, ratio):
    d = {k: v * ratio for k, v in data.items() if k not in ('percent')}
    d['percent'] = data['percent']
    return d


def main(arguments):
    debug = arguments.get('--verbose') or False
    change_logging_level(debug)

    json_folder = arguments.get('--json') or None
    html_path = arguments.get('--output') or "dashboard.html"

    logger.info("Generating Dashboard.")

    # load global statistics
    with open(os.path.join(json_folder, 'statistics.json')) as f:
        statistics = OrderedDict(sorted(json.load(f).items(), key=tssort))

    # update stats with price data
    for key in statistics.keys():
        if key == 'relayers':
            continue
        statistics[key]['stats']['estimated_price'] = \
            estimated_price_for(statistics[key], statistics['relayers'])
        statistics[key]['stats']['estimated_vat'] = \
            multiply_items(statistics[key]['stats']['estimated_price'], 0.18)
        statistics[key]['stats']['estimated_price_total'] = \
            multiply_items(statistics[key]['stats']['estimated_price'], 1.18)

    # load daily total for each month
    def loadjs(key):
        with open(os.path.join(json_folder, '{}.json'.format(key)), 'r') as f:
            return OrderedDict(sorted(json.load(f).items(), key=tssort))
    daily_data = {
        key: loadjs(key) for key in statistics.keys()
        if key not in ('total', 'relayers')
    }

    # cumulative values for each days
    with open(os.path.join(json_folder, 'cumulative.json')) as f:
        cumulative = OrderedDict(sorted(json.load(f).items(), key=tssort))

    # list of fields to loop on
    fields = OrderedDict([
        ('nb_sms_total', "Nombre SMS TOTAL"),
        ('nb_sms_in', "Nombre SMS Entrant"),
        ('nb_sms_out', "Nombre SMS Sortant"),
        ('nb_messages_total', "Nombre Messages TOTAL"),
        ('nb_messages_in', "Nombre Messages Entrant"),
        ('nb_messages_out', "Nombre Messages Sortant"),
        ('estimated_price', "Coût estimatif HT"),
        ('estimated_vat', "Coût estimatif TVA"),
        ('estimated_price_total', "Coût estimatif TTC"),
    ])

    # prepare context
    context = {
        'update_time': datetime_from_iso(
            statistics['total']['update_time']).strftime('%d %B %Y, %Hh%I'),
        'relayers': statistics['relayers'],
        'months_data': {k: v for k, v in statistics.items()
                        if k != 'relayers'},
        'daily_data': daily_data,
        'cumulative': cumulative,
        'fields': fields,
        'orange_id': ORANGE,
        'malitel_id': MALITEL,
        'orange_key': text_type(ORANGE),
        'malitel_key': text_type(MALITEL),
        'amount_fields': [k for k in fields.keys()
                          if k.startswith('estimated_')]
    }

    # render template in file
    template = jinja_env.get_template('dashboard_tmpl.html')
    with open(html_path, 'w') as f:
        f.write(template.render(**context))


if __name__ == '__main__':
    main(docopt(help, version=0.1))
