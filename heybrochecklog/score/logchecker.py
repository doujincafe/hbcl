"""A module which contains the base log checker, with the code shared between
more specific log checkers.
"""

import re

from heybrochecklog import UnrecognizedException
from heybrochecklog.resources import VERSIONS
from heybrochecklog.score.modules import drives, parsers, validation
from heybrochecklog.shared import format_pattern as fmt_ptn


class LogChecker:
    """The base log checker to be subclassed by more specific log checkers."""

    def __init__(self, patterns, translation=None, markup=False):
        self.patterns = patterns
        self.translation = translation
        self.markup = markup

    def verify_version(self, regex, line, ripper):
        """Verify that the version of the log is legitimate."""
        result = regex.search(line)
        if result:
            version, date = result.group(1), result.group(2)
            if (version, date) in VERSIONS[ripper]:
                return version
        raise UnrecognizedException('Unrecognized {} version'.format(ripper))

    def get_drive(self, regex, line):
        """Get the name of the ripping drive used."""
        re_drive = re.compile(fmt_ptn(self.patterns['drive']) + regex)
        result = re_drive.match(line)
        if result:
            return result.group(1).strip()
        raise UnrecognizedException('Could not parse ripping drive')

    def index_log(self, log, ninety_five=False):
        """Index key line numbers inside the log."""
        if ninety_five:
            read_mode = re.compile(re.sub(' +', ' ', fmt_ptn(self.translation['1234'])))
        else:
            read_mode = re.compile(fmt_ptn(self.patterns['settings']['Read mode']))
        toc = (
            re.compile(fmt_ptn(self.patterns['toc']))
            if 'toc' in self.patterns
            else None
        )

        for i, line in enumerate(log.contents):
            if log.index_settings is None and read_mode.match(line):
                log.index_settings = i
            elif log.index_toc is None and 'toc' in self.patterns and toc.match(line):
                log.index_toc = i
            elif self.all_range_index(log, line):
                self.all_range_index_action(log, i)
            elif re.match(fmt_ptn(self.patterns['track']) + r' [0-9]+$', line):
                log.track_indices.append(i)

        self.validate_indices(log)

    def validate_indices(self, log):
        """Validate the indices of notable lines in the log."""
        if not log.track_indices:
            raise UnrecognizedException('No tracks found')

        # +4 to compensate for range rip lines
        for i in range(max(log.track_indices) + 4, len(log.contents)):
            # Need to check the full_contents and add the extra space for AR summary leading space.
            if re.match(r' ?\w', log.full_contents[i]):
                log.track_indices.append(i - 1)
                log.index_footer = i
                break

        log.index_tracks = min(log.track_indices)
        if not log.index_toc:
            log.index_toc = log.index_tracks

    def all_range_index(self, log, line):
        """Match the All Tracks or Range Rip line, depending on subclassed ripper."""
        pass

    def all_range_index_action(self, log, line_num):
        """Action to take when detection of the All Tracks or Range Rip line occurs."""
        pass

    def evaluate_settings(self, log):
        """Evaluate the log for usage of proper rip settings."""
        psettings = self.patterns['settings']
        proper_settings = self.patterns['proper settings']

        # Compile regex beforehand
        settings = {}
        colon = r' : (.*)' if log.language == 'english' else r'(?: :)? : (.*)'
        for key, setting in psettings.items():
            settings[key] = re.compile(fmt_ptn(setting) + colon)

        # Iterate through line in the settings, and verify each setting in `sets` dict
        for line in log.contents[log.index_settings : log.index_toc]:
            for key, setting in list(settings.items()):
                result = setting.search(line)
                if result and key == 'Drive offset':
                    drives.eval_offset(log, result.group(1))
                    del settings[key]
                elif result:
                    if not re.search(fmt_ptn(proper_settings[key]), result.group(1)):
                        log.add_deduction(key)
                    del settings[key]
                    break

            self.check_bad_settings(log, line)

        self.evaluate_unmatched_settings(log, settings)

    def check_bad_settings(self, log, line):
        """Evaluate the bad settings, override in subclass if desired."""
        pass

    def evaluate_unmatched_settings(self, log, settings):
        """Evaluate all unmatched settings and deduct for them."""
        for key in settings:
            if log.range and key == 'Gap handling':
                log.add_deduction('Could not verify gap handling')
            elif key == 'Gap handling':
                log.add_deduction('Gap handling')
            elif key == 'ID3 tags':
                log.add_deduction('Could not verify presence of ID3 tags')
            elif key == 'Null samples':
                log.add_deduction('Could not verify usage of null samples')
            else:
                raise UnrecognizedException(
                    'One or more required settings could not be found'
                )

    def analyze_tracks(self, log, track_settings, parse_errors, accuraterip=True):
        """Get track data for each track and check for errors."""
        ar_patterns = self.patterns['accuraterip'].items() if accuraterip else {}
        err_patterns = self.patterns['track errors'].items()

        for i, index in enumerate(log.track_indices):
            track_data = {}
            track_num = parsers.get_track_number(log, index, self.patterns['track'])

            for line in log.contents[log.track_indices[i] : log.track_indices[i + 1]]:
                # Collect the track data using the track_settings list.
                parsers.parse_settings(track_data, track_settings, line)
                # Log the AccurateRip results - add AR status to log.accuraterip list.
                if accuraterip:
                    parsers.parse_accuraterip(log, ar_patterns, line)
                # Ripping Errors - Loop through errors in json track errors.
                parse_errors(log, err_patterns, track_num, line)

            validation.check_crc_mismatch(log, track_num, track_data)

            log.tracks[track_num] = track_data
            if log.track_indices[i + 1] == max(log.track_indices):
                break

        self.evaluate_tracks(log)

    def evaluate_tracks(self, log):
        """Evaluate the analyzed track data for deficiencies (actually split off the
        logchecker-specific) stuff ;)
        """
        pass

    def deduct_and_score(self, log):
        """Process the accumulated deductions and score the log file."""
        if log.crc_mismatch:
            log.add_deduction('CRC mismatch', len(log.crc_mismatch))

        # Sum all the deductions and calculate score
        log.score -= sum(
            [de[1] for de in log.deductions.values() if isinstance(de[1], int)]
        )
