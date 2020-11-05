import os
from pathlib import Path

import pytest
from heybrochecklog.score import score_log

"""Lazy person not going to do full unit testing."""

LOGS = [
    (
        'had-decoding-issues.log',
        {
            'EAC 0.95 log or older (-30 points)',
            'EAC <1.0 (no checksum)',
            'Gaps were not analyzed and appended (-10 points)',
        },
    ),
    (
        'also-bad.log',
        {
            'Combined read/write offset cannot be verified (-5 points)',
            'Test & Copy was not used (-20 points)',
            'EAC 0.95 log or older (-30 points)',
            'EAC <1.0 (no checksum)',
            'Gaps were not analyzed and appended (-10 points)',
        },
    ),
    (
        'bad-settings.log',
        {
            'Combined read/write offset cannot be verified (-5 points)',
            'C2 pointers were used (-20 points)',
            'EAC 0.95 log or older (-30 points)',
            'EAC <1.0 (no checksum)',
            'Gaps were not analyzed and appended (-10 points)',
        },
    ),
    (
        'read-mode.log',
        {
            'Audio cache not defeated (-10 points)',
            'EAC 0.95 log or older (-30 points)',
            'EAC <1.0 (no checksum)',
            'Gaps were not analyzed and appended (-10 points)',
        },
    ),
    (
        'burst.log',
        {
            'The drive could not be found in the database; however, an offset of 0 is rarely correct (-5 points)',  # noqa E501
            'Read mode was not secure (-20 points)',
            'C2 pointers were used (-20 points)',
            'Accurate stream was not used (-20 points)',
            'Audio cache not defeated (-10 points)',
            'Test & Copy was not used (-20 points)',
            'EAC 0.95 log or older (-30 points)',
            'EAC <1.0 (no checksum)',
            'Gaps were not analyzed and appended (-10 points)',
        },
    ),
]


@pytest.mark.parametrize('filename, deductions', LOGS)
def test_scoring(filename, deductions):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'EAC95', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert deductions == {d[0] for d in log['deductions']}


@pytest.mark.parametrize('filename', [log_tuple[0] for log_tuple in LOGS])
def test_markup(filename):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'EAC95', filename)
    log_file = Path(log_path)
    log = score_log(log_file, markup=True)

    markup_path = os.path.join(
        os.path.dirname(__file__),
        'logs',
        'EAC95',
        'markup',
        '{}.markup'.format(filename),
    )
    with open(markup_path, 'r') as markup_file:
        markup_contents = markup_file.read()

    assert log['contents'] == markup_contents
