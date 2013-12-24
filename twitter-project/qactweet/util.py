"""Various utility functions."""


import datetime
import httplib
import re
import socket
import urlparse


def isoformat(date_string, fmt='%a %b %d %H:%M:%S +0000 %Y'):
    """Convert a Twitter date string to ISO-formatted date string."""
    return datetime.datetime.strptime(date_string, fmt).isoformat()


def strip_tags(html):
    """Return the given HTML without tags.

    Adapted from: http://stackoverflow.com/a/4869782
    """
    return re.sub('<[^<]+?>', '', html)


def unshorten(url, _redirects=0):
    """Recursively unshorten a URL.

    Sends an HTTP HEAD request to the URL. If the response code is 20x,
    the URL is not redirected and recursion stops. If the response code
    is 30x, send an HTTP HEAD request to the URL in the `Location`
    header field.

    Adapted from: http://stackoverflow.com/a/4201180

    Args:
        url: A string URL, including the scheme (usually http).
        _redirects: An internal variable used for recursion.

    Returns:
        For a non-redirected (HTTP 20x) or redirected (HTTP 30x) url,
            the target URL.

    Raises:
        IOError: For too many redirects, an error response code (HTTP
            4xx or 5xx), a malformed header, or an HTTP error (such as
            a connection error or invalid URL).
    """
    if _redirects > 3:
        raise IOError('Too many redirects')
    try:
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        resp = h.getresponse()
        if resp.status / 100 == 2:
            return url
        elif resp.status / 100 == 3 and resp.getheader('Location'):
            url = resp.getheader('Location')
            return self.unshorten(url, _redirects + 1)
        else:
            raise IOError('Encountered HTTP error or malformed header')
    except (httplib.HTTPException, socket.gaierror):
        raise IOError('Encountered HTTP error or URL error')


