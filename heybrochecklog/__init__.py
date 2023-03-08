class UnrecognizedException(Exception):
    pass


import argparse  # noqa: E402
from pathlib import Path  # noqa: E402

from heybrochecklog.score import score_log  # noqa: E402
from heybrochecklog.translate import translate_log  # noqa: E402


def parse_args():
    """Parse arguments."""
    description = 'Tool to analyze, translate, and score a CD Rip Log.'

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('log', help='log file to check.', nargs='+')
    parser.add_argument(
        '-t',
        '--translate',
        help='translate a foreign log to English',
        action='store_true',
    )
    parser.add_argument(
        '-m',
        '--markup',
        help='print the marked up version of the log after analyzing',
        action='store_true',
    )
    parser.add_argument(
        '-s',
        '--score-only',
        help='Only print the score of the log.',
        action='store_true',
    )

    return parser.parse_args()


def runner():
    """Main function to handle command line usage of the heybrochecklog package."""
    args = parse_args()
    for log_path in args.log:
        log_file = Path(log_path)
        if not log_file.is_file():
            print('{} does not exist.'.format(log_path))
        elif args.translate:
            translate_(args, log_file, log_path)
        elif args.log:
            score_(args, log_file, log_path)


def score_(args, log_file, log_path):
    log = score_log(log_file, args.markup)
    if args.score_only:
        if not log['unrecognized']:
            print(log['score'])
        else:
            print('Log is unrecognized: {}'.format(log['unrecognized']))
    else:
        try:
            print(format_score(log_path, log, args.markup))
        except UnicodeEncodeError as error:
            print('Cannot encode logpath: {}'.format(error))


def translate_(args, log_file, log_path):
    log = translate_log(log_file)
    try:
        print(format_translation(log_path, log))
    except UnicodeEncodeError as error:
        print('Cannot encode logpath: {}'.format(error))


def format_score(logpath, log, markup):
    """Turn a log file JSON into a pretty string."""
    output = []
    output.append('\nLog: ' + logpath)
    if log['unrecognized']:
        output.append('\nLog is unrecognized: {}'.format(log['unrecognized']))
    else:
        if log['flagged']:
            output.append('\nLog is flagged: {}'.format(log['flagged']))
        output.append('\nDisc name: {}'.format(log['name']))
        output.append('\nScore: {}'.format(log['score']))

        if log['deductions']:
            output.append('\nDeductions:')
            for deduction in log['deductions']:
                output.append('  >>  {}'.format(deduction[0]))

        if markup:
            output.append('\n\nStylized Log:\n\n{}'.format(log['contents']))

    return '\n'.join(output)


def format_translation(logpath, log):
    """Turn a translated log JSON into a pretty string."""
    output = []
    output.append('\nLog: ' + logpath)

    if log['unrecognized']:
        output.append('\nFailed to recognize log. {}'.format(log['unrecognized']))
    elif log['language'] == 'english':
        output.append('\nLog is already in English!')
    else:
        output.append('\nOriginal language: {}'.format(log['language']).title())
        output.append('\n---------------------------------------------------')
        output.append('\n' + log['log'])

    return '\n'.join(output)
