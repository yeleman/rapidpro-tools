#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime
import json
import os
from collections import OrderedDict

from docopt import docopt

from rapidpro_tools import logger, change_logging_level
from rapidpro_tools.utils import (
    datetime_to_iso, datetime_from_iso, end_of_day, end_of_month,
    nb_sms_for_messages, safe_percent, period_middle, in_period,
    jsdthandler, js_timestamp, namesort)
from rapidpro_tools.mongo import messages, relayers

destdir = ''

help = ("""Usage: export-message-stats.py [-v] [-h] <destdir>

-h --help                       Display this help message
-v --verbose                    Display DEBUG messages
<destdir>                       Folder for writing JSON files to.

This script exports monthly + daily messages count stats in JSON """)


def get_relayers():
    return relayers.find()


def get_periods(start_on, end_on):
    logger.debug("get_periods({}, {})".format(start_on, end_on))

    periods = {
        'months': {},
        'days': {}
    }

    current = start_on
    while current < end_on:
        month = {
            'name': current.strftime('%Y-%m'),
            'start_on': datetime.datetime(
                current.year, current.month, current.day),
            'end_on': end_of_month(current.year, current.month)
        }
        month['middle'] = period_middle(month['start_on'], month['end_on'])
        month['middle_ts'] = js_timestamp(month['middle'])
        if month['name'] not in periods['months'].keys():
            periods['months'].update({month['name']: month})

        day = {
            'name': current.strftime('%Y-%m-%d'),
            'start_on': current,
            'end_on': end_of_day(current.year, current.month, current.day)
        }
        day['middle'] = period_middle(day['start_on'], day['end_on'])
        day['middle_ts'] = js_timestamp(day['middle'])
        if day['name'] not in periods['days'].keys():
            periods['days'].update({day['name']: day})

        current = current + datetime.timedelta(days=1)
        if current.second:
            current = datetime.datetime(current.year,
                                        current.month,
                                        current.day)
    return periods


def query_dict_for(period):
    period_start = datetime_to_iso(period['start_on'])
    period_end = datetime_to_iso(period['end_on'])
    return {
        'created_on': {'$gte': period_start,
                       '$lte': period_end}
    }


def statistics_for(period):
    logger.debug("statistics_for({})".format(period))

    def dup(adict, bdict):
        d = adict.copy()
        d.update(bdict)
        return d

    query = dup({'status': {'$ne': 'F'}}, query_dict_for(period))
    query_in = dup(query, {'direction': 'I'})
    query_out = dup(query, {'direction': 'O'})
    period_messages = messages.find(query)
    relayer_ids = [r['relayer'] for r in get_relayers()]

    stats = {
        'nb_messages_in': {
            'percent': {},
            'total': messages.find(query_in).count()},
        'nb_messages_out': {
            'percent': {},
            'total': messages.find(query_out).count()},
        'nb_messages_total': {
            'percent': {},
            'total': period_messages.count()},
        'nb_sms_in': {
            'percent': {},
            'total': nb_sms_for_messages(messages.find(query_in))},
        'nb_sms_out': {
            'percent': {},
            'total': nb_sms_for_messages(messages.find(query_out))},
        'nb_sms_total': {
            'percent': {},
            'total': nb_sms_for_messages(period_messages)},
    }

    for relayer_id in relayer_ids:
        relayer_query = dup(query, {'relayer': relayer_id})
        relayer_query_in = dup(relayer_query, {'direction': 'I'})
        relayer_query_out = dup(relayer_query, {'direction': 'O'})
        filtered = messages.find(relayer_query)

        # messages are straight numbers from rapidpro
        stats['nb_messages_total'][relayer_id] = filtered.count()
        stats['nb_messages_in'][relayer_id] = \
            messages.find(relayer_query_in).count()
        stats['nb_messages_out'][relayer_id] = \
            messages.find(relayer_query_out).count()

        # SMS are computed to count multiparts
        stats['nb_sms_total'][relayer_id] = nb_sms_for_messages(
            filtered)
        stats['nb_sms_in'][relayer_id] = nb_sms_for_messages(
            messages.find(relayer_query_in))
        stats['nb_sms_out'][relayer_id] = nb_sms_for_messages(
            messages.find(relayer_query_out))

    # update percentages
    for field in stats.keys():
        for relayer_id in relayer_ids:
            stats[field]['percent'][relayer_id] = safe_percent(
                stats[field][relayer_id], stats[field]['total'])

    return stats


def get_relayers_details():
    return {
        relayer['relayer']: {
            k: v for k, v in relayer.items()
            if k != '_id'}
        for relayer in relayers.find()
    }


def get_grand_total(start_on, end_on):
    mperiod = {'name': "GRAND TOTAL", 'start_on': start_on, 'end_on': end_on}
    mperiod['middle'] = period_middle(mperiod['start_on'], mperiod['end_on'])
    mperiod['middle_ts'] = js_timestamp(mperiod['middle'])
    return period_stats(mperiod)


def period_stats(period):
    d = period.copy()
    d.update({'stats': statistics_for(period)})
    return d


def get_months_stats(periods):
    return {
        period['name']: period_stats(period)
        for period in sorted(periods['months'].values(), key=namesort)
    }


def generate_periods_stats(destdir='', start_on=None, end_on=None):

    # when the DB is empty
    if not messages.count():
        logger.error("No messages in DB. wrong config?")
        return

    # no start_on? use first message date
    if start_on is None:
        start_on = datetime_from_iso(
            messages.find().sort([('id', 1)]).limit(1)[0].get('created_on'))

    if end_on is None:
        end_on = datetime_from_iso(
            messages.find().sort([('id', -1)]).limit(1)[0].get('created_on'))

    periods = get_periods(start_on=start_on, end_on=end_on)

    # single statistics file with entries for each month
    logger.info("Generating all-periods stats by months")
    statistics = get_months_stats(periods)
    statistics.update({
        'relayers': get_relayers_details(),
        'total': get_grand_total(start_on, end_on)
    })
    statistics['total'].update({'update_time': datetime.datetime.now()})
    with open(os.path.join(destdir,
                           'statistics.json'), 'w') as statistics_io:
        json.dump(statistics, statistics_io, indent=4, default=jsdthandler)

    # one stats file per month with entries for each day
    for period in sorted(periods['months'].values(), key=namesort):
        logger.info("Generating {} stats by days".format(period['name']))
        month_stats = OrderedDict([
            (dperiod['name'], period_stats(dperiod))
            for dperiod in sorted(periods['days'].values(), key=namesort)
            if in_period(period, dperiod['middle'])
        ])
        with open(os.path.join(destdir,
                               '{}.json'.format(period['name'])), 'w') as io:
            json.dump(month_stats, io, indent=4, default=jsdthandler)

    # single cumulative stats file
    logger.info("Generating cumulative stats by days")

    def cperiod_for(period):
        p = period.copy()
        p.update({
            'start_on': start_on,
            'middle': period_middle(p['start_on'], p['end_on']),
            'middle_ts': js_timestamp(p['middle'])
        })
        return p
    with open(os.path.join(destdir,
                           'cumulative.json'), 'w') as io:
        cumul_stats = OrderedDict([
            (period['name'], period_stats(cperiod_for(period)))
            for period in sorted(periods['days'].values(), key=namesort)
        ])
        json.dump(cumul_stats, io, indent=4, default=jsdthandler)


def main(arguments):
    debug = arguments.get('--verbose') or False
    change_logging_level(debug)

    logger.info("Generating JSON exports for message statistics")

    generate_periods_stats(destdir=arguments.get('<destdir>') or None)

    logger.info("All Done.")

if __name__ == '__main__':
    main(docopt(help, version=0.1))
