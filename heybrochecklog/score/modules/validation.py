"""This module contains validation functions for log checking."""

from heybrochecklog import UnrecognizedException


def analyze_accuraterip(log):
    """Analyze the AccurateRip results in the log."""
    if log.accuraterip:
        for ar_result in log.accuraterip:
            if (
                ar_result[0] != log.accuraterip[0][0]
                and (ar_result[1] is not None and log.accuraterip[0][1] is not None)
                and (int(ar_result[1]) >= 5 or int(log.accuraterip[0][1]) >= 5)
            ):
                log.add_deduction('AccurateRip discrepancies')
                break
    elif any('copy crc' in data for tnum, data in log.tracks.items()):
        log.add_deduction('AccurateRip')


def check_crc_mismatch(log, track_num, track_data):
    """Check a track block for a CRC mismatch."""
    if all(data in track_data for data in ['test crc', 'copy crc']):
        if track_data['test crc'] != track_data['copy crc']:
            log.crc_mismatch.append(track_num)


def validate_track_count(log):
    """Verify the presence of all tracks and check for a data track."""
    if not log.range:
        # Data tracks have one extra ToC entry, but one less ripped track
        if max(log.tracks.keys()) + 1 == max(log.toc.keys()):
            log.add_deduction('Data track detected')
        elif len(log.tracks) != len(log.toc):
            if not log.ripper == 'XLD' or not log.has_deduction('HTOA extracted'):
                raise UnrecognizedException('Not all tracks are represented in the log')


def validate_track_settings(log, xld=False):
    """Also verify that each track contains the required data."""
    if xld:
        if log.range:
            required_settings = ['copy crc']
        else:
            required_settings = ['filename', 'copy crc']
    else:
        required_settings = ['filename', 'peak', 'copy crc']

    for track in log.tracks:
        if track in log.track_errors['Aborted copy']:
            pass
        elif not all(setting in log.tracks[track] for setting in required_settings):
            raise UnrecognizedException(
                'Unable to confirm presence of required track data'
            )

    # Check for Test & Copy and CRC Mismatches
    if not all('test crc' in track for track in log.tracks.values()):
        if log.has_deduction('HTOA extracted') or log.has_deduction(
            'HTOA not ripped twice'
        ):
            # Verify that every track minus HTOA is T&C (Range based is index 0)
            if all('test crc' in track for i, track in log.tracks.items() if i):
                return
        log.add_deduction('Test & Copy')
