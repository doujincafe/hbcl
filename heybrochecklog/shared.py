"""This module contains shared functions between the various top-level modules."""

import codecs
import json
import os

import chardet


def get_log_contents(log_file):
    """Open a log file and return its contents."""
    encoding = get_log_encoding(log_file)
    with log_file.open(encoding=encoding) as log:
        contents = log.readlines()

    return contents


def get_log_encoding(log_file):
    """Get the encoding of the log file with the chardet library."""
    raw = log_file.read_bytes()
    if raw.startswith(codecs.BOM_UTF8):
        return 'utf-8-sig'
    else:
        result = chardet.detect(raw)
        return result['encoding'] if result['confidence'] > 0.7 else 'utf-8-sig'


def format_pattern(pattern, append=None):
    if append:
        pattern = [p + append for p in pattern]
    return '|'.join(pattern)


def open_json(*paths):
    """Open the language JSON patterns file and return it."""
    basepath = get_path()
    with open(os.path.join(basepath, 'resources', *paths)) as jsonfile:
        language_data = json.load(jsonfile)

    return language_data


def get_path():
    """Get the filepath for the heybrochecklog package directory."""
    return os.path.abspath(os.path.dirname(__file__))
