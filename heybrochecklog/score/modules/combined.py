"""This module contains the functions which deal with combined logs."""

import re

from heybrochecklog.logfile import LogFile


def split_combined(log):
    """Split a combined log into an array of logs. If there is a single
    log, return a list with one log inside it. Not relevant for XLD.
    """
    logs = []

    # Create a list of indices for combined log markers. By default # includes indices 0 and len()
    log_indices = (
        [0]
        + [
            i + 2
            for i, line in enumerate(log.full_contents)
            if re.match(r'-{60}', line)
        ]
        + [len(log.full_contents)]
    )

    # Split the log files. Create new log object for each log.
    for i, line in enumerate(log_indices):
        new_log = LogFile(
            log.full_contents[line : (log_indices[i + 1])], ripper=log.ripper
        )
        logs.append(new_log)

        # Return the array of logs if the end index of section is
        # equivalent to the length of the original log.
        if log_indices[i + 1] == max(log_indices):
            break

    return logs


def defragment(logs, eac95=False):
    """Re-combine split combined logs."""
    if len(logs) == 1 and not logs[0].htoa:
        return logs[0]

    full_contents = []
    for log in logs:
        full_contents += log.full_contents
    logs[0].full_contents = full_contents

    # Make sure HTOA CRC's match if they exist.
    if not eac95:
        htoa_logs = [log for log in logs if log.htoa]
        if htoa_logs:
            analyze_htoa(logs, htoa_logs)

    # Iterate through each log and patch the original log's data where new data exists.
    # logs[0] is used as the base log and returned at the end.
    for log in logs[1:]:
        # Make sure the albums have the same name.
        if log.album != logs[0].album:
            return logs[0]

        sub_settings(logs, log)
        sub_double_copy(logs, log)
        if not log.range:
            sub_track_errors(logs, log)

    # Remove HTOA detection if it was extracted.
    if not eac95:
        patch_htoa(logs, htoa_logs)

    if len(logs) > 1:
        logs[0].add_deduction('Combined log')

    return logs[0]


def sub_settings(logs, log):
    """Check settings of newer rip; add new deductions and pop fixed deductions."""
    # Remove the deductions from the first log if they aren't present in the final log,
    # but verify the number of tracks is consistent between the two.
    for deduction in logs[0].deductions.copy():
        if not log.has_deduction(deduction) and len(log.tracks) == len(logs[0].tracks):
            logs[0].remove_deduction(deduction)
    # Add additional deductions from the newer log to the older log.
    for deduction in log.deductions.copy():
        if not logs[0].has_deduction(deduction):
            logs[0].add_deduction(deduction)


def sub_double_copy(logs, log):
    """Check two copy only rips and score as T&C Rip."""
    if logs[0].has_deduction('Test & Copy') and len(logs[0].tracks) == len(log.tracks):
        for new_track, original_track in zip(
            log.tracks.values(), logs[0].tracks.values()
        ):
            if 'copy crc' in new_track and 'copy crc' in original_track:
                if new_track['copy crc'] != original_track['copy crc']:
                    break
        else:
            logs[0].remove_deduction('Test & Copy')


def sub_track_errors(logs, log):
    """Substitute newer ripped track data for older ripped track data."""
    for track in log.tracks:
        # Don't substitute track errors for aborted copies.
        if 'copy crc' in log.tracks[track]:
            logs[0].tracks[track] = log.tracks[track]
            replace_accumulated_errors(track, logs, log)
            replace_crc_mismatches(track, logs, log)


def replace_accumulated_errors(track, logs, log):
    """Replace accumulated track errors."""
    for error in logs[0].track_errors:
        if track in log.track_errors[error]:
            continue
        for i, original_track in enumerate(logs[0].track_errors[error]):
            if track == original_track:
                logs[0].track_errors[error].pop(i)


def replace_crc_mismatches(track, logs, log):
    """Replace CRC mismatch errors."""
    if track not in log.crc_mismatch:
        for i, original_track in enumerate(logs[0].crc_mismatch):
            if track == original_track:
                logs[0].crc_mismatch.pop(i)


def analyze_htoa(logs, htoa_logs):
    """Analyze potential HTOA rips to and add deductions for CRCs and T&C."""
    # Remove htoa logs from logs list
    logs = [log for log in logs if log not in htoa_logs]

    if len(htoa_logs) >= 2:
        matches = [
            log
            for log in htoa_logs[1:]
            if log.tracks[0]['copy crc'] == htoa_logs[0].tracks[0]['copy crc']
        ]
        if not matches:
            htoa_logs[0].add_deduction('CRC mismatch on HTOA extraction')
    elif len(htoa_logs) == 1:
        htoa_logs[0].add_deduction('HTOA not ripped twice')

    htoa_logs[0].remove_deduction('Test & Copy')
    logs.append(htoa_logs[0])


def patch_htoa(logs, htoa_logs):
    """Adjust the HTOA deductions based on the defragmented log."""
    htoa_ripped = any(log for log in htoa_logs if log.htoa_ripped)

    if htoa_ripped and logs[0].has_deduction('HTOA detected'):
        logs[0].remove_deduction('HTOA detected not extracted')

    if logs[0].has_deductions('Improper HTOA extraction', 'HTOA extracted'):
        logs[0].remove_deduction('HTOA extracted')
