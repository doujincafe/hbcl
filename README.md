# hey-bro-check-log

[![Come on Join us!](https://img.shields.io/badge/Discord-Come%20on%20Join%20us!-7289da)](https://discord.gg/mC4Yp6J)
![Github Actions Badge](https://github.com/doujinmusic/hbcl/actions/workflows/main.yml/badge.svg)

This version of hey-bro-check-log is maintained by doujin music discord community.

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
