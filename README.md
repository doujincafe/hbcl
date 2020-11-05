# hey-bro-check-log

[![Build Status](https://travis-ci.org/ligh7s/hey-bro-check-log.svg?branch=master)](https://travis-ci.org/ligh7s/hey-bro-check-log)

A python tool which analyzes and verifies good ripping practices and potential inaccuracies
in CD ripping logs.

## Support

- Supports checking EAC and XLD logs.
- Matches deductions on Redacted (minus stupid aggregate ones)
- Supports combined EAC logs
- Detects other irregularities and special occurrences in the rip
  - Data tracks
  - Irregular AR results
  - Hidden tracks and extraction
- Foreign language support (temperamental, as it's based on the most recent translation files).

## Running CLI

```
usage: heybrochecklog [-h] [-t] [-m] [-s] log

Tool to analyze, translate, and score a CD Rip Log.

positional arguments:
  log               log file to check.

optional arguments:
  -h, --help        show this help message and exit
  -t, --translate   translate a foreign log to English
  -m, --markup      print the marked up version of the log after analyzing
  -s, --score-only  Only print the score of the log.
```
