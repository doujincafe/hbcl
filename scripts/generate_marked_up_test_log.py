#!/usr/bin/env python3

import sys
from os import path
from pathlib import Path

from heybrochecklog.score import score_log

for log_path in sys.argv[1:]:
    log_file = Path(log_path)
    if not log_file.is_file():
        print('{} does not exist.'.format(log_path))
        continue

    log = score_log(log_file, markup=True)
    dir_, file_name = path.split(log_path)
    output_path = path.join(dir_, 'markup', file_name + '.markup')

    with open(output_path, 'w') as output_file:
        output_file.write(log['contents'])

    print('Wrote marked up log to {}.'.format(output_path))
