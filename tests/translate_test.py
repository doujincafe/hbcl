import os
from pathlib import Path

import pytest
from heybrochecklog.translate import translate_log

LOGS = [
    ('french-big-calm.log'),
]


@pytest.mark.parametrize('filename', LOGS)
def test_translation(filename):
    log_path = os.path.join(os.path.dirname(__file__), 'logs', 'translations', filename)
    log_file = Path(log_path)
    log = translate_log(log_file)

    translated_path = os.path.join(
        os.path.dirname(__file__),
        'logs',
        'translations',
        'translated',
        '{}.translated'.format(filename),
    )
    with open(translated_path, 'r') as translated_file:
        translated_contents = translated_file.read()

    assert log['log'] == translated_contents
