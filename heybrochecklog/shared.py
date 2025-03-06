"""This module contains shared functions between the various top-level modules."""

import codecs
import json
import os

import cchardet
import chardet


def get_log_contents(log_file):
    """Open a log file and return its contents."""
    encoding = get_log_encoding(log_file)
    with log_file.open(encoding=encoding) as log:
        contents = log.readlines()

    return contents


def detect_chardet(log_data):
    cchardet_detection = cchardet.detect(log_data)
    chardet_detection = chardet.detect(log_data)

    """In cases chardet spews out Windows-1252 as encoding, switch over to cchardet."""
    if chardet_detection['encoding'] == "Windows-1252":
        return cchardet_detection

    """When chardet has higher confidence than cchardet, then we will use chardet."""
    if (chardet_detection['confidence'] or 0) > (cchardet_detection['confidence'] or 0):
        return chardet_detection

    return cchardet_detection


def get_log_encoding(log_file):
    """Get the encoding of the log file with the chardet library."""
    raw = log_file.read_bytes()
    if raw.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    else:
        result = detect_chardet(raw)
        return result['encoding'] if (result['confidence'] or 0) > 0.7 else 'utf-8-sig'


def format_pattern(pattern, append=None):
    if append:
        pattern = [p + append for p in pattern]
    return '|'.join(pattern)


def format_pattern_for_setting_evaluation(pattern):
    return '(?:{})'.format('|'.join(pattern))


def open_json(*paths):
    """Open the language JSON patterns file and return it."""
    basepath = get_path()
    with open(os.path.join(basepath, 'resources', *paths)) as jsonfile:
        language_data = json.load(jsonfile)

    return language_data


def get_path():
    """Get the filepath for the heybrochecklog package directory."""
    return os.path.abspath(os.path.dirname(__file__))
