import os
from pathlib import Path

import pytest
from heybrochecklog.score import score_log

"""Lazy person not going to do full unit testing."""

LOGS = [
    (
        'cdparanoia.log',
        {
            'Ripper mode was not XLD Secure Ripper (-100 points)',
            'C2 pointers were used (-20 points)',
            'Gaps were not analyzed and appended (-10 points)',
            'XLD pre-142.2 (no checksum)',
            'Track gain was not turned on (-1 points)',
        },
    ),
    ('crc-mismatch.log', {'CRC mismatch (-30 points)'}),
    ('htoa.log', {'CD-R detected; not a pressed CD', 'HTOA extracted'}),
    (
        'ripping-error.log',
        {
            'Track 16: Damaged sector (724 occurrences) (-10 points)',
            'CRC mismatch (-30 points)',
        },
    ),
    ('range-vbox.log', {'Range rip detected (-20 points)'}),
    ('bad-chardet-no-checksum.log', {'No checksum (-15 points)'}),
    ('cdr-multi-filename.log', {'CD-R detected; not a pressed CD'}),
    (
        'xld-cdp.log',
        {
            'Ripper mode was not XLD Secure Ripper (-100 points)',
            'XLD pre-142.2 (no checksum)',
        },
    ),
]


@pytest.mark.parametrize('filename, deductions', LOGS)
def test_scoring(filename, deductions):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'XLD', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert deductions == {d[0] for d in log['deductions']}


@pytest.mark.parametrize('filename', [log_tuple[0] for log_tuple in LOGS])
def test_markup(filename):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'XLD', filename)
    log_file = Path(log_path)
    log = score_log(log_file, markup=True)

    markup_path = os.path.join(
        os.path.dirname(__file__), 'logs', 'XLD', 'markup', '{}.markup'.format(filename)
    )
    with open(markup_path, 'r') as markup_file:
        markup_contents = markup_file.read()

    assert log['contents'] == markup_contents
