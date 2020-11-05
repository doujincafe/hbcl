"""This module contains the LogFile class, an encapsulation of log variables."""

import re

from heybrochecklog.resources import DEDUCTIONS


class LogFile:
    """A log file class containing variables, score, deductions, etc."""

    def __init__(self, contents, ripper=None):

        self.full_contents = contents
        self.contents = format_full_contents(contents)
        self.concat_contents = [line for line in self.contents if line.strip()]
        self.score = 100
        self.ripper = ripper
        self.language = None
        self.drive = None
        self.version = None
        self.album = None
        self.unrecognized = None

        # Some other log settings
        self.range = False
        self.cdr = False
        self.unindexed_drive = False
        self.htoa = False
        self.htoa_index = False
        self.htoa_ripped = False

        # Important parts of the log
        self.checksum = False
        self.all_tracks = None
        self.deductions = {}
        self.crc_mismatch = []
        self.track_errors = {
            "Aborted copy": [],
            "Timing problem": [],
            "Suspicious position": [],
            "Missing samples": [],
            "Read error": [],
            "Damaged sector count": [],
        }

        # Lists of data for the log
        self.toc = {}
        self.accuraterip = []
        self.track_indices = []
        self.tracks = {}

        # Indexes of log locations
        self.index_settings = None
        self.index_toc = None
        self.index_tracks = None
        self.index_footer = None

        # Flagged = auto report log
        self.flagged = False

    def to_dict(self):
        """Return a dict of the log analysis."""
        if self.unrecognized:
            return {
                'unrecognized': self.unrecognized,
                'flagged': self.flagged,
                'contents': ''.join(self.full_contents),
            }

        deductions = [deduction for deduction in self.deductions.values()]

        return {
            'deductions': deductions,
            'flagged': self.flagged,
            'name': self.album,
            'ripper': self.ripper,
            'score': self.score,
            'version': self.version,
            'unrecognized': False,
            'contents': ''.join(self.full_contents),
        }

    def add_deduction(
        self, deduction, multiplier=1, track=None, extra_phrase=None, cap_10=False
    ):
        """Add a deduction to the log file."""
        name, score = self._get_deduction_from_dict(deduction)
        if score:
            score = score * multiplier if not cap_10 else score * min(10, multiplier)

        if track:
            name = 'Track {}: {}'.format(track, name)
        if multiplier > 1:
            name += ' ({} occurrences)'.format(multiplier)
        if score:
            name += ' (-{} points)'.format(score)
        if extra_phrase:
            name += ' ({})'.format(extra_phrase)

        self.deductions[deduction] = [name, score]

    def _get_deduction_from_dict(self, deduction):
        """Get the deduction's name and score from the deductions dict."""
        if deduction not in DEDUCTIONS:
            return (deduction, None)

        deduction_entry = DEDUCTIONS[deduction]
        # Some deductions are different per-ripper and are represented
        # with an extra embedded dictionary.
        if isinstance(deduction_entry, dict):
            if self.ripper in deduction_entry:
                deduction_entry = deduction_entry[self.ripper]
            else:
                deduction_entry = deduction_entry['Default']

        return (deduction_entry[0], deduction_entry[1])

    def remove_deduction(self, deduction):
        """Remove a deduction from the log file."""
        if deduction in self.deductions:
            del self.deductions[deduction]

    def has_deduction(self, deduction):
        """Learn whether or not the log file has a deduction."""
        return deduction in self.deductions

    def has_deductions(self, *deductions):
        """Return whether or not log has every deduction in deductions."""
        return all(de in self.deductions for de in deductions)


def format_full_contents(full_contents):
    """
    Format raw contents by stripping spaces, blank lines, and filtering
    out unicode crap.
    """
    contents = [re.sub(r'\s+', ' ', l.rstrip()) for l in full_contents]
    contents = [re.sub('：', ':', l) for l in contents]
    contents = [re.sub('，', ', ', l) for l in contents]

    return contents
