"""This module contains the generation functions for dicts of to-match lines
when marking up log files.
"""

import html
import re

from heybrochecklog.shared import format_pattern as fmt_ptn


def eac_track_matches(translation):
    """Generate the list of to-match lines from translations."""
    source_one = {
        'log4': ['1269', '1270', '1217', '1299', '1227', '1218'],
        'good': ['1220', '1281'],
        'crc': ['1271', '1272'],
    }
    source_two = {
        'log3': ['1221'],
        'badish': ['1330', '1283', '1210', '1211'],
        'bad': ['1212', '1213', '1214', '1215', '1216', '1228'],
    }
    return {
        **generate_match_type(translation, source_one),
        **generate_match_type(translation, source_two, append='.*'),
    }


def xld_track_matches():
    """Return a dictionary containing the XLD matches."""
    return {
        'full_line': [
            ['log4', 'Statistics'],
            ['good', '-&gt;Accurately ripped'],
            ['badish', '-&gt;Track not present in AccurateRip database'],
            ['bad', '-&gt;Rip may not be accurate'],
            ['bad', 'List of damaged sector positions +:'],
            ['badish', r'\(\d+\) \d{2}:\d{2}:\d{2}'],
            ['log3', r'\/.+\.(?:[Ff][Ll][Aa][Cc]|[Ww][Aa][Vv]|[Mm][Pp]3|[Aa][Aa][Cc])'],
        ],
        'crc': [r'CRC32 hash \(test run\)', 'CRC32 hash'],
        'statistics': {
            'bad': [
                'Read error',
                r'Skipped \(treated as error\)',
                'Inconsistency in error sectors',
                'Damaged sector count',
            ],
            'badish': [
                r'Jitter error \(maybe fixed\)',
                'Retry sector count',
                r'Edge jitter error \(maybe fixed\)',
                r'Atom jitter error \(maybe fixed\)',
                r'Drift error \(maybe fixed\)',
                r'Dropped bytes error \(maybe fixed\)',
                r'Duplicated bytes error \(maybe fixed\)',
            ],
        },
    }


def eac_footer_matches(translation):
    """Matches for the EAC footer block."""
    source = {
        'good': ['1336', '1222', '1225'],
        'badish': ['1333', '1334', '1344', '1335'],
        'bad': ['1284', '1224'],
        'log4 log5': ['1275'],
    }
    matches = generate_match_type(translation, source)

    # AccurateRip stuff
    source = {'good': ['1340'], 'badish': ['1339', '1341'], 'bad': ['1342', '1343']}
    matches = generate_match_type(translation, source, matches=matches, prepend='.+')

    if '1290' in translation:
        ar_prepend = r'{} +\d+ +'.format(translation['1290'])
        source = {'good': ['1277'], 'badish': ['1279'], 'bad': ['1276', '1278']}
        matches = generate_match_type(
            translation, source, matches=matches, prepend=ar_prepend, append='.+'
        )

    # Checksum stuff
    if '1325' in translation:
        matches['good'].append('==== {} [0-9A-F]+ ===='.format(translation['1325']))

    # EAC HAS A TYPO FOR "NO ERRORS OCCURED" WTF
    if translation['1222'] == 'No errors occurred':
        matches['good'].append('No errors occured')

    return matches


def xld_footer_matches():
    """Matches for the XLD footer block."""
    return {
        'good': ['No errors occurred', 'End of status report'],
        'badish': ['Some inconsistencies found'],
    }


def xld_ar_summary():
    """Matches for the XLD AccurateRip Summary block."""
    return {
        'good': [
            r'Track \d+ : OK.+',
            html.escape('-&gt;All tracks accurately ripped.*'),
        ],
        'badish': [
            r'Track \d+ : NG.+',
            'Disc not found in AccurateRip DB',
            r'-&gt;\d+ tracks? accurately ripped, \d+ tracks? not',
        ],
        'log4 log5': ['AccurateRip Summary'],
    }


def generate_match_type(translation, source, matches=None, prepend='', append=''):
    """Function to generate the match types."""
    matches = {} if not matches else matches
    for match_type in source.keys():
        if match_type not in matches:
            matches[match_type] = []
        for line_id in source[match_type]:
            if line_id in translation:
                match = prepend + re_paren(translation[line_id]) + append
                matches[match_type].append(html.escape(match))

    return matches


def re_paren(line):
    """Regex the comma. Quality docstring."""
    line = re.sub(r'\(', r'\(', fmt_ptn(line))
    return re.sub(r'\)', r'\)', line)
