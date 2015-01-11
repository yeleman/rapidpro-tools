#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import math

from rapidpro_tools import logger
from rapidpro_tools.mongo import db, contacts
from rapidpro_tools.utils import post_api_data
from rapidpro_mali import ORANGE, MALITEL, relayer_from_number

numbers = db['numbers']


def is_ureporter(number):
    return bool(contacts.find({'phone': "+223{}".format(number)}).count())


def remove_number(number):
    return numbers.remove({'number': number})


def send_invitation(relayer, number_list):
    max_num = 100
    for it in range(0, int(math.ceil(len(number_list) / max_num))):
        step = it * max_num
        chunk = number_list[step:step + max_num]

        logger.info(".. sending {} invitations at once.".format(len(chunk)))

        post_api_data('/messages.json', {
            'phone': ["+223{}".format(num) for num in chunk],
            'text': "Bonjour, tu es invité à rejoindre U-report pour partager "
                    "tes opinions avec la jeunesse malienne. Pour t'inscrire, "
                    "envoie \"MALI\" au 36019. C'est 100% gratuit.",
            'relayer': relayer
        })


def main():
    pending_contacts = numbers.find({'sent': False})
    logger.info("We have {} potential numbers..."
                .format(pending_contacts.count()))

    to_send = {
        ORANGE: [],
        MALITEL: [],
    }

    for number_item in pending_contacts:
        logger.info(number_item['number'])
        if not is_ureporter(number_item['number']):

            relayer = relayer_from_number(number_item['number'])
            if not relayer:
                continue

            to_send[relayer].append(number_item['number'])

            number_item.update({'sent': True})
            numbers.save(number_item)
        else:
            remove_number(number_item['number'])

    logger.info("Sending {} invitations to Orange users..."
                .format(len(to_send[ORANGE])))
    send_invitation(ORANGE, to_send[ORANGE])

    logger.info("Sending {} invitations to Malitel users..."
                .format(len(to_send[MALITEL])))
    send_invitation(MALITEL, to_send[MALITEL])

if __name__ == '__main__':
    main()
