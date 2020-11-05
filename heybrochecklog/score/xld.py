"""This module contains the XLD Log Checker."""

import re

from heybrochecklog import UnrecognizedException
from heybrochecklog.markup import markup
from heybrochecklog.score.logchecker import LogChecker
from heybrochecklog.score.modules import parsers, validation
from heybrochecklog.shared import format_pattern as fmt_ptn


class XLDChecker(LogChecker):
    """This class analyzes XLD Log Files."""

    def check(self, log):
        """Checks the XLD logs."""
        if len(log.contents) < 25:
            raise UnrecognizedException('Cannot parse log file; log file too short')

        log.version = self.check_version(log)
        log.album = log.concat_contents[2]
        log.drive = self.check_drive(log)
        self.check_cdr(log)

        self.index_log(log)
        self.evaluate_settings(log)
        parsers.index_toc(log)
        self.check_tracks(log)
        self.is_there_a_htoa(log)
        validation.validate_track_count(log)
        validation.validate_track_settings(log, xld=True)
        parsers.parse_checksum(
            log, self.patterns['checksum'], '20121222', 'XLD pre-142.2'
        )

        self.deduct_and_score(log)
        if self.markup:
            markup(log, self.patterns, self.translation)

        return log

    def check_version(self, log):
        """Check the version of the log and verify it is acceptable."""
        regex = re.compile(r'X Lossless Decoder version ([0-9abc]+) \(([0-9\.]+)\)')
        return self.verify_version(regex, log.concat_contents[0], 'XLD')

    def check_drive(self, log):
        """Check the drive of the log and verify it is an allowed drive."""
        regex = r' *: (.*)?(?: +\(revision [A-Z0-9\.]\))?$'
        return self.get_drive(regex, log.concat_contents[3])

    def check_cdr(self, log):
        """Check the log to see if CD-R is flagged."""
        result = re.search(
            fmt_ptn(self.patterns['disc type']) + r' : (.*)', log.concat_contents[4],
        )
        if result:
            if result.group(1) == 'Pressed CD':
                return
            elif result.group(1) == 'CD-Recordable':
                log.cdr = True
                log.flagged = True
                log.add_deduction('CD-R')
            else:
                raise UnrecognizedException('Unknown disc type')

    def all_range_index(self, log, line):
        """Match the Range Rip line in the log file."""
        if log.all_tracks is None and re.match(
            fmt_ptn(self.patterns['All Tracks']), line
        ):
            return True
        return False

    def all_range_index_action(self, log, line_num):
        """Action to take when the range rip line is matched."""
        log.all_tracks = line_num

    def is_there_a_htoa(self, log):
        """Check rip for Hidden Track One Audio."""
        # 450 sectors or 6 seconds minimum, one track rip with pregap (containing HTOA)
        # appended to the first track. It is then split from the first track with
        # Audacity/Audition.
        if len(log.tracks) == 1 and log.toc[1][0] >= 450:
            for line in log.contents[log.index_settings : log.index_toc]:
                if re.match(r'Gap status +: Analyzed, Appended$', line):
                    log.add_deduction('HTOA extracted')
                    break

    def check_tracks(self, log):
        """Get track data for each track and check for errors."""
        tsettings = self.patterns['track settings']
        track_settings = {
            'filename': re.compile(
                r'\s+' + fmt_ptn(tsettings['filename']) + r' : (.*?\/.*?\..*)'
            ),
            'pregap': re.compile(
                r'\s+' + fmt_ptn(tsettings['pregap']) + r' : ([0-9:\.]+)'
            ),
            'gain': re.compile(
                r'\s+' + fmt_ptn(tsettings['gain']) + r' : ([A-Za-z0-9\.-]+)'
            ),
            'peak': re.compile(r'\s+' + fmt_ptn(tsettings['peak']) + r' : ([0-9\.]+)'),
            'test crc': re.compile(
                r'\s+' + fmt_ptn(tsettings['test crc']) + r' : ([A-Z0-9]{8})'
            ),
            'copy crc': re.compile(
                r'\s+' + fmt_ptn(tsettings['copy crc']) + r' : ([A-Z0-9]{8})'
            ),
        }

        if log.all_tracks:
            for i in range(log.all_tracks, min(log.track_indices)):
                if re.match(track_settings['filename'], log.contents[i]):
                    log.range = True
                    break

        self.analyze_tracks(log, track_settings, parsers.parse_errors_xld)

    def evaluate_tracks(self, log):
        """Evaluate the analyzed track data for deficiencies (actually split off the
        logchecker-specific) stuff ;)
        """
        # Deduct for a Range Rip
        if log.range:
            log.add_deduction('Range rip')

        # Check AccurateRip - Mismatching AR results can indicate problems even with T&C
        validation.analyze_accuraterip(log)

    def deduct_and_score(self, log):
        """Process the accumulated deductions and score the log file."""
        # Check for presence of Track gain in the tracks.
        if not all('gain' in log.tracks[track] for track in log.tracks):
            log.add_deduction('Track gain')

        # Deduct for accumulated per-track XLD deductions; since XLD
        # accumulated deductions are deducted by an occurrence basis, we are
        # splitting deductions into one deduction per track, capped at 10%.
        for error in log.track_errors:
            for each in log.track_errors[error]:
                log.add_deduction(error, multiplier=each[1], track=each[0], cap_10=True)

        super().deduct_and_score(log)
