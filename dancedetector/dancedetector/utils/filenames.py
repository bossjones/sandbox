# -*- encoding: utf-8 -*-
#
# Author: Massimo Menichinelli
# Homepage: http://www.openp2pdesign.org
# License: MIT
#

import logging
import string

from dancedetector.dbx_logger import get_logger  # noqa: E402

## Required packages


LOGGER = get_logger(__name__, provider="Filenames", level=logging.DEBUG)


# https://gist.github.com/seanh/93666
def format_filename(s):
    """Take a string and return a valid filename constructed from the string.
    Uses a whitelist approach: any characters not present in valid_chars are
    removed. Also spaces are replaced with underscores.

    Note: this method may produce invalid filenames such as ``, `.` or `..`
    When I use this method I prepend a date string like '2009_01_15_19_46_32_'
    and append a file extension like '.txt', so I avoid the potential of using
    an invalid filename.
    """
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = "".join(c for c in s if c in valid_chars)
    filename = filename.replace(" ", "_")  # I don't like spaces in filenames.
    LOGGER.debug(f"filename after being sanatized = {filename}")
    return filename
