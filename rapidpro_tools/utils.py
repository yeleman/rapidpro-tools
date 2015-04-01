#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import math
import datetime
import json
import re

import iso8601
import requests

from rapidpro_tools import CONFIG, logger

UTC = iso8601.iso8601.Utc()
ASCII_MAX_CHARS = 160
UNICODE_MAX_CHARS = 72
TIMEOUT = 120

jsdthandler = lambda obj: obj.isoformat() \
    if isinstance(obj, datetime.datetime) \
    else json.JSONEncoder().default(obj)


namesort = lambda x: x['name']
tssort = lambda x: int(x[1].get('middle_ts', '0'))


def datetime_is_aware(adate):
    return adate.tzinfo is not None


def datetime_aware(adate):
    if datetime_is_aware(adate):
        return adate
    return adate.replace(tzinfo=UTC)


def datetime_from_iso(aniso):
    if aniso is None:
        return None
    return iso8601.parse_date(aniso).replace(tzinfo=None)


def datetime_to_iso(adate):
    if datetime_is_aware(adate):
        adate = adate.replace(tzinfo=None)
    isf = adate.isoformat()
    if '.' not in isf:
        isf += '.0000'
    return isf


def end_of_month(year, month):
    nmonth = month + 1 if month != 12 else 1
    nyear = year if month != 12 else year + 1
    return datetime.datetime(nyear, nmonth, 1) - datetime.timedelta(seconds=1)


def end_of_day(year, month, day):
    return datetime.datetime(year, month, day) \
        + datetime.timedelta(days=1) \
        - datetime.timedelta(seconds=1)


def period_middle(start, end):
    return start + (end - start) // 2


def js_timestamp(adate):
    return '{}000'.format(adate.strftime('%s'))


def is_ascii(text):
    try:
        text.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False


def nb_sms_for_message(message_dict):
    text = message_dict.get("text")
    if len(text) < UNICODE_MAX_CHARS:
        return 1

    # nb_max = ASCII_MAX_CHARS if is_ascii(text) else UNICODE_MAX_CHARS
    nb_max = ASCII_MAX_CHARS \
        if not CONFIG['relayers_unicode'] else UNICODE_MAX_CHARS
    return int(math.ceil(len(text) / nb_max))


def nb_sms_for_messages(cursor):
    return sum([nb_sms_for_message(m) for m in cursor])


def safe_percent(nomin, denomin, default=0):
    try:
        return nomin / denomin
    except ZeroDivisionError:
        return default


def in_period(period, adate):
    return adate >= period['start_on'] and adate <= period['end_on']


def get_api_data(url_or_path, **params):
    headers = {'Authorization': "Token {}".format(CONFIG.get("api_token"))}
    if url_or_path.startswith('http'):
        url = url_or_path
    else:
        url = "{server}{path}" \
              .format(server=CONFIG.get('server_url'), path=url_or_path)
    logger.debug("URL: {}?{}".format(
        url, "&".join(["{key}={val}".format(key=key, val=val)
                       for key, val in params.items()])))
    try:
        r = requests.get(url=url, headers=headers, params=params,
                         timeout=TIMEOUT)
        assert r.status_code == requests.codes.ok
    except AssertionError:
        if r.status_code in (403, 401):
            logger.error(
                "Received {code} HTTP status code. Most likely "
                "a wrong API TOKEN in config ({token})."
                .format(code=r.status_code, token=CONFIG.get('api_token')))
        elif r.status_code == 404:
            logger.error(
                "Received {code} HTTP status code. Most likely "
                "a wrong Server URL in config ({url})."
                .format(code=r.status_code, url=CONFIG.get('server_url')))
        raise
    except Exception as e:
        logger.error("Unhandled Exception while requesting data.")
        logger.exception(e)
        raise
    else:
        return r.json()


def post_api_data(url_or_path, payload):
    headers = {'Authorization': "Token {}".format(CONFIG.get("api_token")),
               'Content-type': 'application/json'}
    if url_or_path.startswith('http'):
        url = url_or_path
    else:
        url = "{server}{path}" \
              .format(server=CONFIG.get('server_url'), path=url_or_path)
    logger.debug("URL: {}".format(url))
    try:
        r = requests.post(url=url, headers=headers,
                          data=json.dumps(payload), timeout=TIMEOUT)
        assert r.status_code in (200, 201)
    except AssertionError:
        if r.status_code in (403, 401):
            logger.error(
                "Received {code} HTTP status code. Most likely "
                "a wrong API TOKEN in config ({token})."
                .format(code=r.status_code, token=CONFIG.get('api_token')))
        elif r.status_code == 404:
            logger.error(
                "Received {code} HTTP status code. Most likely "
                "a wrong Server URL in config ({url})."
                .format(code=r.status_code, url=CONFIG.get('server_url')))
        else:
            logger.error("Received unexcpected {code} HTTP status code."
                         .format(code=r.status_code))
            raise
    except Exception as e:
        logger.error("Unhandled Exception while requesting data.")
        logger.exception(e)
        raise
    else:
        return r.json()


def import_path(name, failsafe=False):
    """ import a callable from full module.callable name """
    def _imp(name):
        modname, __, attr = name.rpartition('.')
        if not modname:
            # single module name
            return __import__(attr)
        m = __import__(modname, fromlist=[str(attr)])
        return getattr(m, attr)
    try:
        return _imp(name)
    except (ImportError, AttributeError) as exp:
        # logger.debug("Failed to import {}: {}".format(name, exp))
        if failsafe:
            return None
        raise exp


def phone_to_name(phone):
    return " ".join(
        [p for p in re.split(r'([0-9]{2})', phone.replace('+223', '')) if p])
