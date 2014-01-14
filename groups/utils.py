#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import phonenumbers

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def normalize_number(msisdn=None, country_code=None):
    """ given a msisdn, return in E164 format """
    assert msisdn is not None
    if (hasattr(settings, 'COUNTRY_CODE') and settings.COUNTRY_CODE):
        country_code = settings.COUNTRY_CODE
    elif country_code is None:
        raise ImproperlyConfigured('must have COUNTRY_CODE in settings or '
                                   'provided as argument')

    num = phonenumbers.parse(msisdn, country_code)
    is_valid = phonenumbers.is_valid_number(num)
    if not is_valid:
        return False
    return phonenumbers.format_number(num,
                                      phonenumbers.PhoneNumberFormat.E164)


def format_number(number, country_code=None):
    return normalize_number(number, country_code) or number
