"""Mark up the log file with classes according to the regex."""

import html
import re

from heybrochecklog.markup.matches import (
    eac_footer_matches,
    eac_track_matches,
    xld_ar_summary,
    xld_footer_matches,
    xld_track_matches,
)
from heybrochecklog.score.modules import parsers
from heybrochecklog.shared import format_pattern as fmt_ptn

VERSIONS = {
    'EAC': r'Exact Audio Copy (V.*) from (.*)',
    'XLD': r'X Lossless Decoder version ([0-9abc]+) \(([0-9\.]+)\)',
}


def markup(log, patterns, translation):
    """Mark up log files with highlighting for proper/improper settings."""
    log.full_contents = [html.escape(line) for line in log.full_contents]

    header(log, translation)
    settings(log, patterns)
    toc(log)
    tracks(log, patterns, translation)
    footer(log, translation)


def header(log, translation):
    """Mark up the header of the log."""
    # If first line is a version line, style it.
    start_index = 0
    if log.ripper in VERSIONS:
        log.full_contents[0] = substitute(
            log.full_contents[0], VERSIONS[log.ripper], 'log1'
        )
        start_index = 1  # No need to scan this line twice.

    if log.ripper == 'EAC' or log.ripper == 'EAC95':
        re_time_line = translation['1274']
    else:  # XLD
        re_time_line = 'XLD extraction logfile from'

    count = 1
    for i, line in enumerate(log.full_contents[start_index : log.index_settings]):
        i += start_index
        # Style the extraction time line.
        if line.strip():
            if count == 1:
                line = substitute(line, '{} (.*)'.format(re_time_line), 'log5')
                log.full_contents[i] = substitute(
                    line, '({}.*)'.format(re_time_line), 'good'
                )
                count += 1
            # Style the Artist / Album string
            elif count == 2:
                log.full_contents[i] = substitute(line, '(.*)', 'log4')
                count += 1
            # Style drive line
            elif count == 3:
                log.full_contents[i] = drive(log, line)
                count += 1
            # XLD CD Type line
            elif count == 4:
                log.full_contents[i] = cd_type(log, line)
                break


def drive(log, line):
    """Mark up the drive line according to offset."""
    if log.has_deduction('Virtual drive'):
        return style_setting(line, 'bad')
    elif log.unindexed_drive:
        line = line.rstrip()
        line += ' (not found in database)\n'
        return style_setting(line, 'badish')
    return style_setting(line, 'good')


def cd_type(log, line):
    """Style CD type line."""
    if log.cdr:
        return style_setting(line, 'badish')
    return style_setting(line, 'good')


def settings(log, patterns):
    """Mark up the settings block."""
    for i, line in enumerate(log.full_contents[log.index_settings : log.index_toc]):
        i += log.index_settings
        if (
            re.match(fmt_ptn(patterns['settings']['Read mode']), line)
            and log.ripper == 'EAC95'
        ):
            log.full_contents[i] = style_95_read_mode(line, patterns)
            continue
        for key, value in patterns['settings'].items():
            if re.match(fmt_ptn(value), line.lstrip()):  # lstrip() for EAC95
                class_ = 'bad' if log.has_deduction(key) else 'good'
                log.full_contents[i] = style_setting(line, class_)
                break
        else:
            if log.ripper in ['EAC', 'EAC95']:
                for key, value in patterns['bad settings'].items():
                    if re.match(fmt_ptn(value), line.lstrip()):
                        log.full_contents[i] = style_setting(line, 'bad')
                        break
                else:
                    log.full_contents[i] = style_setting(line, 'log4')
            else:
                log.full_contents[i] = style_setting(line, 'log4')


def toc(log):
    """Mark up TOC block."""
    # Mark up beginning of block
    init_line = log.full_contents[log.index_toc]
    log.full_contents[log.index_toc] = substitute(init_line, '(.*)', 'log4 log5')

    # Adjust line for XLD All Tracks block
    end_line = log.all_tracks if log.all_tracks else log.index_tracks
    if log.ripper == 'XLD':  # XLD AR Summary block matches
        matches = xld_ar_summary()

    re_toc_title = re.compile(
        r' +[^0-9]+ +\| +[^0-9]+ +\| +[^0-9]+ +\| +[^0-9]+ +\| +[^0-9]+ *$'
    )
    re_toc_entry = (
        r' +[0-9]+ +\| +([0-9:\.]+) +\| +([0-9:\.]+) +\| +([0-9]+) +\| +([0-9]+) *$'
    )
    for i, line in enumerate(log.full_contents[log.index_toc : end_line]):
        i += log.index_toc
        if re_toc_title.match(line):
            log.full_contents[i] = sub_strong(line, '(.*)')
        elif re.match(r'\s+-+\s*$', line):
            log.full_contents[i] = sub_strong(line, '(-+)')
        elif re.match(re_toc_entry, line):
            log.full_contents[i] = sub_toc(line)

        # XLD also has an AR Summary block.
        if log.ripper == 'XLD':
            for class_ in matches:
                for element in matches[class_]:
                    if re.match(element, line.lstrip()):
                        log.full_contents[i] = substitute(
                            line, '({})'.format(element), class_
                        )


def tracks(log, patterns, translation):
    """Mark up the tracks block."""
    if log.ripper == 'XLD':
        xld_tracks(log, patterns)
    else:
        eac_tracks(log, patterns, translation)


def xld_tracks(log, patterns):
    """XLD tracks."""
    matches = xld_track_matches()
    indices = (
        [log.all_tracks] + log.track_indices if log.all_tracks else log.track_indices
    )

    for i, index in enumerate(indices):
        track_num, log.full_contents[index] = track_number(
            log, index, patterns['track']
        )
        for j, line in enumerate(log.full_contents[indices[i] : indices[i + 1]]):
            j += indices[i]
            for match in matches['full_line']:
                if re.match(match[1], line.lstrip()):
                    log.full_contents[j] = substitute(
                        line, '({}.*)'.format(match[1]), match[0]
                    )
                    break
            else:
                for match in matches['crc']:
                    if re.match(match + ' +:', line.lstrip()) and track_num:
                        track = log.tracks[track_num]
                        log.full_contents[j] = sub_crc(
                            track, match, line, xld_colon=True
                        )
                        break
                else:
                    found = False
                    for class_ in matches['statistics']:
                        for element in matches['statistics'][class_]:
                            if re.match(element, line.lstrip()):
                                log.full_contents[j] = style_statistic(line, class_)
                                found = True
                                break
                        if found:
                            break
                    else:
                        log.full_contents[j] = style_setting(
                            line, 'log3', first_class='log4', include_colon=True
                        )

        if indices[i + 1] == max(indices):
            break


def eac_tracks(log, patterns, translation):
    """EAC tracks."""
    matches = eac_track_matches(translation)

    for i, index in enumerate(log.track_indices):
        track_num, log.full_contents[index] = track_number(
            log, index, patterns['track']
        )
        for j, line in enumerate(
            log.full_contents[log.track_indices[i] : log.track_indices[i + 1]]
        ):
            j += log.track_indices[i]
            for element in matches['log4']:
                if re.match(element, line.lstrip()):
                    line = substitute(line, ' +{} +(.*)'.format(element), 'log3')
                    log.full_contents[j] = substitute(
                        line, ' +({}.+)'.format(element), 'log4'
                    )
                    break
            for class_ in ['good', 'badish', 'bad', 'log3']:
                for element in matches[class_]:
                    if re.match(element, line.lstrip()):
                        log.full_contents[j] = substitute(
                            line, ' *({}.*)'.format(element), class_
                        )
                        break
            for element in matches['crc']:
                if re.match(element, line.lstrip()):
                    track = log.tracks[track_num]
                    log.full_contents[j] = sub_crc(track, element, line)
        if log.track_indices[i + 1] == max(log.track_indices):
            break


def track_number(log, index, track_pattern):
    """Parse track number and style the line."""
    if log.all_tracks and log.full_contents[index].startswith('All Tracks'):
        return (0, substitute(log.full_contents[index], '(.*)', 'log5'))
    track_num = parsers.get_track_number(log, index, track_pattern)
    line = substitute(
        log.full_contents[index], r'{} +(\d+)'.format(track_pattern), 'log4 log1'
    )
    line = substitute(line, '({}.+)'.format(track_pattern), 'log5')
    return (track_num, line)


def sub_crc(track, element, line, xld_colon=False):
    """Process the CRCs for markup."""
    re_crc = '([0-9A-F]{8})'
    if 'test crc' not in track:
        line = substitute(line, re_crc, 'badish')
    elif track['test crc'] != track['copy crc']:
        line = substitute(line, re_crc, 'bad')
    else:
        line = substitute(line, re_crc, 'good')
    if xld_colon:
        return substitute(line, ' +({}.+ :)'.format(element), 'log4')
    return substitute(line, ' +({}.+)'.format(element), 'log4',)


def footer(log, translation):
    """Mark up the footer."""
    matches = (
        xld_footer_matches() if log.ripper == 'XLD' else eac_footer_matches(translation)
    )

    for i, line in enumerate(log.full_contents[log.index_footer :]):
        i += log.index_footer
        for class_ in matches:
            for element in matches[class_]:
                if re.match(element, line.lstrip()):
                    log.full_contents[i] = substitute(
                        line, '({})'.format(element), class_
                    )
                    break
            if log.ripper == 'XLD':
                # XLD Checksum stuff goes here
                if line.startswith('-----BEGIN XLD SIGNATURE-----'):
                    log.full_contents[
                        i
                    ] = '<span class="good">-----BEGIN XLD SIGNATURE-----\n'
                elif line.startswith('-----END XLD SIGNATURE-----'):
                    log.full_contents[i] = '-----END XLD SIGNATURE-----</span>'


def style_setting(line, class_, first_class='log5', include_colon=False):
    """Style a setting line in the log (<setting_name> +: <setting>)."""
    if re.match(r'.+:.+', line):
        parts = line.split(':', 1)
        setting = re.escape(
            parts[0].lstrip() + ':' if include_colon else parts[0].lstrip()
        )
        data = '({})'.format(re.escape(parts[1].strip()))
        line = substitute(line, '({})'.format(setting), first_class)
        line = substitute(line, data, class_)
    return line


def style_statistic(line, class_):
    """Style a XLD statistic line."""
    if re.match(r'.+:.+', line):
        parts = line.split(':', 1)
        statistic = re.escape(parts[0].lstrip() + ':')
        occurrences = parts[1].strip()

        if occurrences.isdigit() and int(occurrences) == 0:
            class_ = 'good'

        line = substitute(line, '({})'.format(occurrences), class_)
        line = substitute(line, '({})'.format(statistic), 'log4')

    return line


def style_95_read_mode(line, patterns):
    """Style the EAC 95 read mode line."""
    # Burst mode doesn't have multiple settings in one line
    if ',' not in line:
        return style_setting(line, 'bad')

    split_line = line.split(':', 1)

    read_mode = split_line[0].rstrip()
    line = line.replace(read_mode, '<span class="log5">{}</span>'.format(read_mode), 1)

    parts = split_line[1].lstrip().split(' ', 1)
    parts[1:] = [part.strip() for part in parts[1].split(',')]
    num = 0
    p = patterns['95 settings']
    for setting in [
        p['Read mode'],
        p['C2 pointers'],
        p['Accurate stream'],
        p['Audio cache'],
    ]:
        if num == len(parts):
            break
        class_ = 'good' if setting in line else 'bad'
        line = line.replace(
            parts[num], '<span class="{}">{}</span>'.format(class_, parts[num]), 1
        )
        num += 1

    return line


def substitute(line, regex, class_):
    """Generate a span and put it in the line per the regex."""
    result = re.search(regex, line)
    if result:
        for match in result.groups():
            line = line.replace(
                match, '<span class="{}">{}</span>'.format(class_, match), 1
            )
    return line


def sub_strong(line, regex):
    """Surround some patterns in <strong> tags."""
    result = re.search(regex, line)
    if result:
        for match in result.groups():
            line = line.replace(match, '<strong>{}</strong>'.format(match), 1)
    return line


def sub_toc(line):
    """Substitute the HTML markup into a line of the TOC."""
    return re.sub(
        r'([0-9]+)( +)\|( +)([0-9:\.]+)( +)\|( +)([0-9:\.]+)( +)\|( +)'
        r'([0-9]+)( +)\|( +)([0-9]+)',
        r'<span class="log4">\1</span>\2<strong>|</strong>'
        r'\3<span class="log1">\4</span>\5<strong>|</strong>'
        r'\6<span class="log1">\7</span>\8<strong>|</strong>'
        r'\9<span class="log1">\10</span>\11<strong>|</strong>'
        r'\12<span class="log1">\13</span>',
        line,
    )


def re_paren(line):
    """Regex the comma. Quality docstring."""
    return re.sub(r'\(', r'\(', line)
