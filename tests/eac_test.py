import os
from pathlib import Path

import pytest
from heybrochecklog.score import score_log

LOGS = [
    ('perf-hunid.log', set()),
    ('1.3-good.log', set()),
    ('abort.log', {'Combined log'}),
    (
        'badcombo.log',
        {'Gaps were not analyzed and appended (-10 points)', 'Combined log'},
    ),
    ('eac-99-good.log', {'EAC <1.0 (no checksum)'}),
    (
        'hella-aborted.log',
        {
            'Audio cache not defeated (-10 points)',
            'Gaps were not analyzed and appended (-10 points)',
            'Could not verify usage of null samples',
            'EAC <1.0 (no checksum)',
            'Could not verify presence of ID3 tags',
            'Combined log',
            'Test & Copy was not used (-20 points)',
        },
    ),
    (
        'bad-htoa.log',
        {
            'Could not verify presence of ID3 tags',
            'HTOA was improperly extracted (-10 points)',
            'HTOA was not ripped twice (-10 points)',
            'Combined log',
        },
    ),
    (
        'range-rip.log',
        {'Could not verify gap handling', 'Range rip detected (-20 points)'},
    ),
    (
        'htoa-not-ripped-twice.log',
        {'HTOA extracted', 'HTOA was not ripped twice (-10 points)'},
    ),
    (
        'shitty.log',
        {
            'Suspicious position (3 occurrences) (-60 points)',
            'CRC mismatch (3 occurrences) (-90 points)',
        },
    ),
    (
        'inconsistent-accuraterip.log',
        {'AccurateRip discrepancies; rip may contain silent errors'},
    ),
    ('negative-offset.log', {'EAC <1.0 (no checksum)'}),
    ('data-track.log', {'EAC <1.0 (no checksum)', 'Data track detected'}),
    ('burst.log', {'Read mode was not secure (-20 points)', 'EAC <1.0 (no checksum)'}),
    (
        'swedish-timing-problems.log',
        {
            'Read mode was not secure (-20 points)',
            'No checksum (-15 points)',
            'Timing problem (-20 points)',
            'CRC mismatch (3 occurrences) (-90 points)',
        },
    ),
    (
        'bad-russian-099.log',
        {
            'Audio cache not defeated (-10 points)',
            'Combined read/write offset cannot be verified (-5 points)',
            'Null samples were not used in CRC calculations (-1 points)',
            'AccurateRip was not enabled (-5 points)',
            'EAC <1.0 (no checksum)',
            'Test & Copy was not used (-20 points)',
        },
    ),
    (
        'fast.log',
        {
            'Read mode was not secure (-20 points)',
            'Could not verify gap handling',
            'Could not verify presence of ID3 tags',
            'Range rip detected (-20 points)',
            'AccurateRip was not enabled (-5 points)',
            'No checksum (-15 points)',
            'Test & Copy was not used (-20 points)',
        },
    ),
    (
        'spanish-log-extra-colons.log',
        {
            'Audio cache not defeated (-10 points)',
            'Gaps were not analyzed and appended (-10 points)',
            'No checksum (-15 points)',
            'Test & Copy was not used (-20 points)',
        },
    ),
    (
        'russian-range-rip-ar-issue.log',
        {
            'Could not verify gap handling',
            'Range rip detected (-20 points)',
            'EAC <1.0 (no checksum)',
            'Test & Copy was not used (-20 points)',
        },
    ),
]


@pytest.mark.parametrize('filename, deductions', LOGS)
def test_scoring(filename, deductions):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'EAC', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert deductions == {d[0] for d in log['deductions']}


@pytest.mark.parametrize('filename', [log_tuple[0] for log_tuple in LOGS])
def test_markup(filename):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'EAC', filename)
    log_file = Path(log_path)
    log = score_log(log_file, markup=True)

    markup_path = os.path.join(
        os.path.dirname(__file__), 'logs', 'EAC', 'markup', '{}.markup'.format(filename)
    )
    with open(markup_path, 'r') as markup_file:
        markup_contents = markup_file.read()

    assert log['contents'] == markup_contents
