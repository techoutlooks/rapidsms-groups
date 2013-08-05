#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import phonenumbers

from django.conf import settings


def normalize_number(msisdn=None):
    """ given a msisdn, return in E164 format """
    assert msisdn is not None
    if (hasattr(settings, 'COUNTRY_CODE') and settings.COUNTRY_CODE):
        num = phonenumbers.parse(msisdn, settings.COUNTRY_CODE)
        is_valid = phonenumbers.is_valid_number(num)
        if not is_valid:
            return None
        return phonenumbers.format_number(num,
                                          phonenumbers.PhoneNumberFormat.E164)
    return None


def format_number(number):
    return normalize_number(number) or number
