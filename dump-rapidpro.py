#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

from docopt import docopt

from rapidpro_tools import logger, change_logging_level
from rapidpro_tools.mongo import (meta, contacts, relayers, messages, runs,
                                  flows, fields)
from rapidpro_tools.utils import get_api_data

help = ("""Usage: dump-rapidpro.py [-v] [-h] [-z] [-a after] [--messages] """
        """[--contacts] [--relayers] [--fields] [--flows] [--runs]

-h --help                       Display this help message
-v --verbose                    Display DEBUG messages
-a --after=<datetime_str>       rapidpro datetime formatted string.
-z --noresume                   Do NOT download where it left (messages)

--relayers                      Dumps all relayers
--contacts                      Dumps all contacts
--messages                      Dumps all messages
--flows                         Dumps all flows
--fields                        Dumps all fields
--runs                          Dumps all runs

This script dumps JSON data from a rapidpro instance into mongo """)


def update_meta(endpoint, updated_on):
    db_item = meta.find_one({'endpoint': endpoint})
    if db_item:
        db_item.update({'updated_on': updated_on})
        meta.save(db_item)
    else:
        meta.insert({'endpoint': endpoint,
                     'updated_on': updated_on})


def update_collection(collection, data, id_field='uuid'):
    if not data['count']:
        return
    for item in data['results']:
        if collection.find({id_field: item.get(id_field)}).count():
            # item exist. update?
            db_item = collection.find_one(
                {id_field: item.get(id_field)})
            db_item.update(item)
            collection.save(db_item)
        else:
            collection.insert(item)
    return


def dump_contacts(**options):
    logger.info("Updating Contacts. Currently have {} contacts in DB."
                .format(contacts.count()))

    # call contacts API
    contacts_list = get_api_data('/contacts.json')
    update_collection(collection=contacts,
                      data=contacts_list,
                      id_field='uuid')

    # loop through potential next pages
    while contacts_list.get('next'):
        contacts_list = get_api_data(contacts_list.get('next'))
        update_collection(collection=contacts,
                          data=contacts_list,
                          id_field='uuid')

    logger.info("Updated Contacts completed. Now have {} contacts in DB."
                .format(contacts.count()))


def dump_relayers(**options):
    logger.info("Updating Relayers. Currently have {} relayers in DB."
                .format(relayers.count()))

    # call relayers API
    relayers_list = get_api_data('/relayers.json')
    update_collection(collection=relayers,
                      data=relayers_list,
                      id_field='relayer')

    # loop through potential next pages
    while relayers_list.get('next'):
        relayers_list = get_api_data(relayers_list.get('next'))
        update_collection(collection=relayers,
                          data=relayers_list,
                          id_field='relayer')

    logger.info("Updated Relayers completed. Now have {} relayers in DB."
                .format(relayers.count()))


def dump_messages(**options):
    logger.info("Updating Messages. Currently have {} messages in DB."
                .format(messages.count()))

    params = {}
    if options.get('after'):
        params.update({'after': options.get('after')})
    elif options.get('resume'):
        if meta.find_one({'endpoint': 'messages'}) is not None:
            params.update({
                'after': meta.find_one({
                    'endpoint': 'messages'}).get('updated_on')})

    # call messages API
    messages_list = get_api_data('/messages.json', **params)
    update_collection(collection=messages,
                      data=messages_list,
                      id_field='id')

    # loop through potential next pages
    while messages_list.get('next'):
        messages_list = get_api_data(messages_list.get('next'))
        update_collection(collection=messages,
                          data=messages_list,
                          id_field='id')

    logger.info("Updated Messages completed. Now have {} messages in DB."
                .format(messages.count()))


def dump_fields(**options):
    logger.info("Updating Fields. Currently have {} fields in DB."
                .format(fields.count()))

    # call fields API
    fields_list = get_api_data('/fields.json')
    update_collection(collection=fields,
                      data=fields_list,
                      id_field='key')

    # loop through potential next pages
    while fields_list.get('next'):
        fields_list = get_api_data(fields_list.get('next'))
        update_collection(collection=fields,
                          data=fields_list,
                          id_field='key')

    logger.info("Updated Fields completed. Now have {} fields in DB."
                .format(fields.count()))


def dump_flows(**options):
    logger.info("Updating Flows. Currently have {} flows in DB."
                .format(flows.count()))

    params = {}
    if options.get('after'):
        params.update({'after': options.get('after')})
    elif options.get('resume'):
        if meta.find_one({'endpoint': 'flows'}) is not None:
            params.update({
                'after': meta.find_one({
                    'endpoint': 'flows'}).get('updated_on')})

    # call flows API
    flows_list = get_api_data('/flows.json', **params)
    update_collection(collection=flows,
                      data=flows_list,
                      id_field='uuid')

    # loop through potential next pages
    while flows_list.get('next'):
        flows_list = get_api_data(flows_list.get('next'))
        update_collection(collection=flows,
                          data=flows_list,
                          id_field='uuid')


def dump_runs(**options):
    logger.info("Updating Runs. Currently have {} runs in DB."
                .format(runs.count()))

    params = {}
    if options.get('after'):
        params.update({'after': options.get('after')})
    elif options.get('resume'):
        if meta.find_one({'endpoint': 'runs'}) is not None:
            params.update({
                'after': meta.find_one({
                    'endpoint': 'runs'}).get('updated_on')})

    # call runs API
    runs_list = get_api_data('/runs.json', **params)
    update_collection(collection=runs,
                      data=runs_list,
                      id_field='run')

    # loop through potential next pages
    while runs_list.get('next'):
        runs_list = get_api_data(runs_list.get('next'))
        update_collection(collection=runs,
                          data=runs_list,
                          id_field='run')

    logger.info("Updated Runs completed. Now have {} runs in DB."
                .format(runs.count()))


def main(arguments):
    debug = arguments.get('--verbose') or False
    change_logging_level(debug)

    logger.info("Starting dump-rapidpro script...{}"
                .format(" [DEBUG mode]" if debug else ""))

    # endpoints
    options = {
        'after': arguments.get('--after') or None,
        'resume': not (arguments.get('--noresume') or False)
    }
    do_contacts = arguments.get('--contacts', False)
    do_messages = arguments.get('--messages', False)
    do_relayers = arguments.get('--relayers', False)
    do_fields = arguments.get('--fields', False)
    do_flows = arguments.get('--flows', False)
    do_runs = arguments.get('--runs', False)

    if not (do_contacts or do_messages or do_relayers
            or do_fields or do_flows or do_runs):
        logger.error("You need to specify at least one action")
        return 1

    if debug:
        logger.debug("Options: {}".format(options))

    now = datetime.datetime.now()
    now_str = now.isoformat()[:-3]

    if do_contacts:
        dump_contacts(**options)
        update_meta('contacts', now_str)

    if do_relayers:
        dump_relayers(**options)
        update_meta('relayers', now_str)

    if do_messages:
        dump_messages(**options)
        update_meta('messages', now_str)

    if do_fields:
        dump_fields(**options)
        update_meta('fields', now_str)

    if do_flows:
        dump_flows(**options)
        update_meta('flows', now_str)

    if do_runs:
        dump_runs(**options)
        update_meta('runs', now_str)

    logger.info("-- All done. :)")


if __name__ == '__main__':
    main(docopt(help, version=0.1))
