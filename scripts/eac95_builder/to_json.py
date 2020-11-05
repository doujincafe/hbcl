#!/usr/bin/env python3

"""
This script takes one or more EAC language files and converts it
into a JSON for the log checker. The resultant .json is named after
the first argument.
"""

import codecs
import json
import os
import re
import sys
from copy import deepcopy
from pathlib import Path

import chardet

import constants
import generators


def main():
    """The main function for the module; handles calling the other functions."""
    language_info = []
    filenames = sys.argv[1:]
    file_contents = read_files(filenames)
    for file_content in file_contents:
        info = {}
        info['patterns'] = deepcopy(constants.SAMPLEPATTERN)
        info['translation'] = {}
        for number, line in regex_the_line(file_content):
            info['translation'][number] = line
        compile_patterns(info)
        language_info.append(info)
    language_info = defragment(language_info)
    dump_json(language_info)


def read_files(paths):
    """Reads the file and returns a list of the file's contents."""
    file_contents = list()
    for path in paths:
        file_ = Path(path)
        if not file_.is_file():
            print(path, 'does not exist! Exiting.')
            exit()

        raw = file_.read_bytes()
        encoding = chardet.detect(raw)['encoding']
        if encoding not in ['UTF-16' or 'iso-8859-1']:
            encoding = 'iso-8859-1'

        try:
            with open(path, 'r', encoding=encoding) as source_file:
                file_content = source_file.readlines()
        except UnicodeDecodeError:
            print('Error decoding', path)
            exit()

        file_contents.append(file_content)

    return file_contents


def regex_the_line(file_contents):
    """Extracts the line number and text from the language file,
    and returns a (#, line) tuple."""
    for line in file_contents:
        result = re.search(r'(\d+)\s=>?\s"(.*)"', line)
        if result:
            number, text = int(result.group(1)), result.group(2).strip()
            if number in constants.LINENUMBERS:
                yield (number, text)


def defragment(language_info):
    real_info = language_info.pop(0)
    for key, val in real_info['patterns'].items():
        if isinstance(val, dict):
            for subkey, subval in val.items():
                if isinstance(subval, str):
                    real_info['patterns'][key][subkey] = [subval]
        elif isinstance(val, str):
            real_info['patterns'][key] = [val]
    for num, line in real_info['translation'].items():
        real_info['translation'][num] = [line]

    for info in language_info:
        real_info['patterns'] = defrag_patterns(real_info['patterns'], info['patterns'])
        for num, line in info['translation'].items():
            if line not in real_info['translation'][num]:
                real_info['translation'][num].append(line)

    return real_info


def defrag_patterns(real_patterns, new_patterns):
    for key, val in new_patterns.items():
        if isinstance(val, str):
            if val not in real_patterns[key]:
                real_patterns[key].append(val)
        elif isinstance(val, dict):
            for subkey, subval in val.items():
                if subval not in real_patterns[key][subkey]:
                    real_patterns[key][subkey].append(subval)

    return real_patterns


def dump_json(language_info):
    """Dump the language file to a JSON."""
    input_filename = os.path.basename(sys.argv[1])
    export_filename = re.sub(r'\..+', '', input_filename).lower()
    file_path = os.path.dirname(os.path.realpath(__file__))
    export_filepath = os.path.join(file_path, '{}.json'.format(export_filename))
    if os.path.exists(export_filepath):
        print('{} already exists, JSON dump canceled.'.format(export_filepath))
    else:
        json_dump = json.dumps(language_info, ensure_ascii=False, indent=4)
        json_dump = re.sub(r'\[\s+(".+")\s+\]', r'[\1]', json_dump, flags=re.MULTILINE)
        with codecs.open(export_filepath, 'w', encoding='utf-8') as jsonfile:
            jsonfile.write(json_dump)


def compile_patterns(language_info):
    """Compile the patterns dict for the language."""
    translation = language_info['translation']
    generators.substitute_translations(language_info['patterns'], translation)
    language_info['patterns']['drive'] = generators.regex_the_drive(translation)
    generators.ninety_five_settings(language_info['patterns'], translation)
    generators.copy_crc_substitution(language_info['patterns'], translation)


if __name__ == '__main__':
    main()
