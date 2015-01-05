#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from docopt import docopt

from rapidpro_tools import logger, change_logging_level
from rapidpro_tools.mongo import contacts
from rapidpro_tools.utils import import_path

help = ("""Usage: update-contacts.py [-v] [-h] -m MODULE

-h --help                       Display this help message
-v --verbose                    Display DEBUG messages

-m --module=<pythonpath>        Dotted Python path to function"""
        """ for individual contact update. Ex: mymodule.myfunction

This script loops all contacts through a passed function """)


def main(arguments):
    debug = arguments.get('--verbose') or False
    change_logging_level(debug)

    logger.info("Starting update-contacts script...{}"
                .format(" [DEBUG mode]" if debug else ""))

    options = {
        'module': arguments.get('--module') or None
    }

    if options['module'] is None:
        logger.error("You must pass in a module.func path.")
        return 1

    try:
        func = import_path(options['module'])
    except Exception as e:
        logger.error("Unable to load function path `{}`"
                     .format(options['module']))
        logger.exception(e)
        return 1
    else:
        if not callable(func):
            logger.error("You func path is not callable `{}`"
                         .format(options['module']))
            return 1

    logger.debug("Options: {}".format(options))

    logger.info("Looping through {} contacts with {}"
                .format(contacts.find().count(), func))
    updated = 0
    for contact in contacts.find():

        if contact['name'] != 'Reg':
            continue

        logger.debug("{}/{}".format(contact['phone'], contact['name']))

        if func(contact):
            updated += 1

    logger.info("Updated {} contacts".format(updated))

    logger.info("-- All done. :)")


if __name__ == '__main__':
    main(docopt(help, version=0.1))
