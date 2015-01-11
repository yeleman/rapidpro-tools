#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import cherrypy
from rapidpro_tools import logger
from rapidpro_tools.mongo import db
from rapidpro_mali import clean_number

numbers = db['numbers']


class UContactReceiver(object):
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def index(self):
        imported = 0
        try:
            all_nums = cherrypy.request.json
            for num in all_nums:
                if handle_number(num):
                    imported += 1
            logger.debug("imported: {}".format(imported))
            return {"status": "ok",
                    "imported": imported}
        except:
            return {"status": "error", "imported": 0}


def handle_number(num):
    num = clean_number(num)
    if not num:
        return

    if numbers.find({'number': num}).count():
        return

    numbers.insert({'number': num, 'sent': False})

    return True


if __name__ == '__main__':
    logger.info("Nb in DB: {}".format(numbers.find({}).count()))
    cherrypy.quickstart(UContactReceiver(), '/', 'app.conf')
