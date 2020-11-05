"""
This module contains the functions which generate the lines that get placed
in the JSON.
"""

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


def ninety_five_settings(patterns, translation):
    """Populate patterns dict with EAC95 settings."""
    # This is going to be messy, with no guarantee of success.
    perf_line = translation[1254]  # The line with optimal settings.

    # Remove `Secure` from string.
    secure, perf_line = perf_line.split(' ', 1)

    # Split the rest of the line by commas.
    rest_of_line = [',' + stri for stri in perf_line.split(',')]
    rest_of_line[0] = rest_of_line[0].lstrip(',')

    if len(rest_of_line) != 3:  # We're looking for two commas here.
        print('Error: ({}) Failed to split EAC95 line. Please fill out manually.'
              .format(translation[1]))
        return

    # Assign the split variables to the patterns dict.
    patterns['settings']['Read mode'] = secure
    patterns['settings']['C2 pointers'] = rest_of_line[0]
    patterns['settings']['Accurate stream'] = rest_of_line[1]
    patterns['settings']['Audio cache'] = rest_of_line[2]


def copy_crc_substitution(patterns, translation):
    """Generate the HTOA line, Copy CRC line."""
    copycrc = translation[1272]
    crc = translation[1219]
    patterns['track settings']['copy crc'] = '(?:{}|{})'.format(copycrc, crc)


def regex_out_paren(line):
    """Regex the comma. Quality docstring."""
    return re.sub(r'\(', r'\(', line)
