# -*- coding: utf-8 -*-


"""Functions for geocoding Tweets."""


import json

import requests


with open('parameters.json') as f:
    p = json.load(f)


def parse_location(location):
    """Parse a Tweet location into a coordinate pair.

    Args:
        location: A string location reported by the Twitter user.

    Returns:
        A (longitude, latitude) float tuple if the location is a valid
            coordinate pair, otherwise (None, None).
    """
    try:
        if location.startswith('iPhone: '):
            return map(float, location[8:].split(','))
        elif location.startswith(u'ÜT: '):
            return map(float, location[4:].split(','))
        else:
            return (None, None)
    except (ValueError, UnicodeEncodeError):
        return (None, None)


def reverse_geocode(lon, lat):
    """Reverse geocode a coordinate pair to a FIPS code.

    This method calls the FCC Census Block Conversions API:
    http://www.fcc.gov/developers/census-block-conversions-api

    The HTTP request includes the email addresses specified in the
    parameters file so that the API maintainers know whom to contact.

    Args:
        lon: A float longitude coordinate.
        lat: A float latitude coordinate.

    Returns:
        A 15-character FIPS code if the coordinate pair is within
            the United States, otherwise None.
    """
    url = 'http://data.fcc.gov/api/block/find'
    payload = {'format': 'json', 'longitude': lon, 'latitude': lat}
    headers = {'from': ''.join(p['email']['recipients'])}
    resp = requests.get(url, params=payload, headers=headers).json()
    return resp['Block']['FIPS']


