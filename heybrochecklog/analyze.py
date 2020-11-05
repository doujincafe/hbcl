"""
This module analyzes the log file and determines generic stuff like
it's ripper and language, etc.
"""

import re

from heybrochecklog import UnrecognizedException
from heybrochecklog.resources import EAC_RIPLINES


def analyze_log(log):
    """Analyze a log file and determine some generic background information."""
    log.ripper = get_ripper(log.contents)
    log.language = determine_language(log)


def get_ripper(contents):
    """Determine the ripper used in the log."""
    if not contents:  # Is file empty?
        raise UnrecognizedException('Empty log file')

    # Even foreign EAC logs start with this line.
    eac_regex = re.compile(r'Exact Audio Copy V[0-1]\.[0-9]+.*?from.*')
    xld_regex = re.compile(r'X Lossless Decoder version ([0-9abc]+) \([0-9\.]+\)')
    if eac_regex.match(contents[0]):
        return 'EAC'
    elif xld_regex.match(contents[0]):
        return 'XLD'
    else:
        # Unfortunately, not all EAC <=0.95 logs are English, so a compiled
        # multi-language ripper regex pattern is necessary.
        re_95 = re.compile('|'.join(list(EAC_RIPLINES.values())))
        if re_95.match(contents[0]):
            return 'EAC95'
        else:
            raise UnrecognizedException('Unrecognized ripper')


def determine_language(log):
    """Determine the language of the log file, and verify that it is an EAC log file."""
    if log.ripper == 'XLD':
        return 'english'

    useful_contents = [
        re.sub(r'\s+', ' ', l.rstrip()) for l in log.contents if l.strip()
    ]
    for line in useful_contents[:2]:
        for language, line_starter in EAC_RIPLINES.items():
            if re.match(line_starter, line):
                return language

    raise UnrecognizedException('Unrecognized/unsupported language')
