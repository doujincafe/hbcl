"""This module contains the functions which deal with drives and offsets."""

import os
import re
import sqlite3

from heybrochecklog import UnrecognizedException
from heybrochecklog.shared import get_path


def eval_offset(log, offset):
    """Validate the offset used by the ripped drive."""
    if not re.match('-?[0-9]+', offset):
        raise UnrecognizedException('Could not parse drive offset.')

    if not offset.startswith('-') and offset != '0':
        offset = '+' + offset

    if check_for_virtual_drives(log):
        log.add_deduction('Virtual drive')
        log.flagged = True
        return

    drivestr = prep_drive_name(log)
    if not drivestr:
        return

    results = drive_db_query(drivestr)
    if not results:
        # Drive not in database
        if offset == '0':
            log.add_deduction('Zero offset')
        log.unindexed_drive = True
        return

    offsets = {row[0] for row in results}
    if offset not in offsets:
        log.add_deduction(
            'Drive offset',
            extra_phrase='correct offsets are: {}'.format(', '.join(offsets)),
        )


def check_for_virtual_drives(log):
    """Check for usage of virtual drives; they aren't good and should be reported."""
    fake_drives = [
        'Generic DVD-ROM SCSI CdRom Device'
        # TODO: Compile a more comprehensive list.
    ]
    if log.drive in fake_drives:
        return True
    return False


def prep_drive_name(log):
    """Prepare the drive name for a DB query."""
    drive = sub_drive_names(log.drive)
    drive_words = re.split(r'[^A-Za-z0-9]+', drive)
    drivestr = '%" AND Name LIKE "%'.join(drive_words)

    return drivestr


def sub_drive_names(drive):
    """Perform regex substitution actions on the drive name for better query results."""
    # Replace generic companies with real companies?
    drive = re.sub(r'JLMS', 'Lite-ON', drive)
    drive = re.sub(r'HL-DT-ST', 'LG Electronics', drive)
    drive = re.sub(r'Matshita', 'MATSHITA', drive)
    drive = re.sub(r'TSSTcorp(BD|CD|DVD)', r'TSSTcorp \1', drive)
    drive = re.sub(r'(\s+-\s|\s+)', ' ', drive)
    return drive


def drive_db_query(drivestr):
    """Query the SQLite3 DB for the drive offset."""
    db_path = os.path.join(get_path(), 'resources', 'drives.db')
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute('SELECT Offset FROM Drives WHERE Name LIKE "%' + drivestr + '%"')
    results = cursor.fetchall()

    conn.close()

    return results
