import os
from pathlib import Path

import pytest
from heybrochecklog.score import score_log

LOGS = [
    ('eac-edited-at-top-extra-spaces.log', 'Unrecognized ripper'),
    ('eac-edited-wrongly-split-combined.log', 'Unrecognized ripper'),
    ('eac-failed-to-properly-forge-a.log', 'Unrecognized/unsupported language'),
    (
        'eac-unrecognized-not-all-tracks.log',
        'Not all tracks are represented in the log',
    ),
    ('eac-wrong-date.log', 'Unrecognized EAC version'),
]


@pytest.mark.parametrize('filename, unrecognized_reason', LOGS)
def test_scoring(filename, unrecognized_reason):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'unrecognized', filename)
    log_file = Path(log_path)
    log = score_log(log_file)
    assert log['unrecognized'] == unrecognized_reason
