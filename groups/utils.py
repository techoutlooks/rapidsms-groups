import phonenumbers

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def normalize_number(msisdn=None, country_codes=None):
    """ given a msisdn, return in E164 format """
    assert msisdn is not None
    if (hasattr(settings, 'COUNTRY_CODES') and settings.COUNTRY_CODES):
        country_codes = settings.COUNTRY_CODES
    elif country_codes is None:
        raise ImproperlyConfigured('must have COUNTRY_CODES in settings or '
                                   'provided as argument')
    if not phonenumbers.SUPPORTED_REGIONS.issuperset(country_codes):
        raise ImproperlyConfigured('invalid COUNTRY_CODES')

    possible_numbers = []
    for country_code in country_codes:
        num = phonenumbers.parse(msisdn, country_code)
        is_valid = phonenumbers.is_valid_number(num)
        if is_valid:
            possible_numbers.append(phonenumbers.format_number(num,
                                    phonenumbers.PhoneNumberFormat.E164))
    # TODO warn if there are several possible numbers!
    if possible_numbers:
        return possible_numbers[0]
    # TODO warn if there are None!
    return None


def format_number(number, country_codes=None):
    return normalize_number(number, country_codes) or number
