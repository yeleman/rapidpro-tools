#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os

from docopt import docopt

from rapidpro_tools import logger, change_logging_level
from rapidpro_tools.contacts import (export_contact_names_to,
                                     fix_contact_names_from)

help = ("""Usage: update-contacts.py [-v] [-h] -f FILE (export|import)

-h --help                       Display this help message
-v --verbose                    Display DEBUG messages

-f --file=<file>                File Path to export/import CSV data to/from

This script exports all contact names to a CSV file or import and update"""
        """ contact names based on a CSV file""")


def main(arguments):
    debug = arguments.get('--verbose') or False
    change_logging_level(debug)

    logger.info("Starting fix-contacts-names script...{}"
                .format(" [DEBUG mode]" if debug else ""))

    options = {
        'export': arguments.get('export') or False,
        'import': arguments.get('import') or False,
        'file': arguments.get('--file') or None,
    }

    if options['export'] + options['import'] != 1:
        logger.error("You must specify whether to export or import data")
        return 1

    if not options['file']:
        logger.error("You must specify a file path")
        return 1

    if options['import'] and not os.path.exists(options['file']):
        logger.error("The filepath `{}` does not exist."
                     .format(options['file']))
        return 1

    if options['export']:
        with open(options['file'], 'w') as fio:
            export_contact_names_to(fio)

    if options['import']:
        with open(options['file'], 'r') as fio:
            fix_contact_names_from(fio)

    logger.info("-- All done. :)")


if __name__ == '__main__':
    main(docopt(help, version=0.1))
