"""This module contains the functions which generate the lines that get placed in the JSON."""

import re  # eeeeeeeeeeeeeeeeeeeee


def substitute_translations(patterns, translation):
    """Substitute the translated strings in for their string IDs."""
    for key, value in patterns.items():
        if isinstance(value, int):
            patterns[key] = remove_colon(translation[value])
        elif isinstance(value, dict):
            for sub_key, sub_value in patterns[key].items():
                if isinstance(sub_value, int):
                    patterns[key][sub_key] = remove_colon(translation[sub_value])


def remove_colon(string):
    """Remove the trailing colon from some lines."""
    string = string.strip()
    string = re.sub(r'\s*(?::|：)\s*', '', string)
    return string


def regex_the_drive(translation):
    """Regex out `Used drive` string from the translation json."""
    drive_string = translation[1233]
    used_drive = remove_colon(drive_string)
    used_drive = re.sub('drive', '[Dd]rive', used_drive)
    return used_drive


def htoa_crc_checksum_substitution(patterns, translation):
    """Generate the HTOA line, Copy CRC line."""
    sel_range = translation[1211]
    sectors = translation[1287]
    copycrc = translation[1272]
    crc = translation[1219]
    checksum = translation[1325] if 1325 in translation else 'Log checksum'

    patterns['htoa'] = r'{} \({} 0-([0-9]+)\)'.format(sel_range, sectors)
    patterns['track settings']['copy crc'] = '(?:{}|{})'.format(copycrc, crc)
    patterns['checksum'] = '==== ' + checksum + ' [A-Z0-9]{64} ===='


def accuraterip(patterns, translation):
    """Append the numbers regex to the AccurateRip lines."""
    # Escape parentheses.
    for key, value in patterns['accuraterip'].items():
        patterns['accuraterip'][key] = regex_out_paren(value)

    # Append confidence regex to AR
    confidence_regex = r' ([0-9]+)\) \[[A-Z0-9]{8}\]'
    patterns['accuraterip']['match'] += confidence_regex
    patterns['accuraterip']['no match'] += ' \\' + translation[1332] + confidence_regex
    patterns['accuraterip']['bad match'] += confidence_regex


def range_accuraterip(patterns, translation):
    """Generate the lines for range rip AccurateRip."""
    confidence_regex = r'([0-9]+)\) \[[A-Z0-9]{8}]'
    track = regex_out_paren(translation[1226])
    accurate = regex_out_paren(translation[1277])
    not_accurate = regex_out_paren(translation[1278])
    not_present = regex_out_paren(translation[1279])

    patterns['range accuraterip']['match'] = '{} [0-9]+ {} {}'.format(track, accurate,
                                                                      confidence_regex)
    patterns['range accuraterip']['no match'] = '{} [0-9]+ {} {}'.format(track, not_accurate,
                                                                         confidence_regex)
    patterns['range accuraterip']['no result'] = '{} [0-9]+ {}'.format(track, not_present)


def regex_out_paren(line):
    """Regex the comma. Quality docstring."""
    return re.sub(r'\(', r'\(', line)
