#!/usr/bin/env python3

"""This script scrapes the AccurateRip offsets page and fills the drive offsests
database with information.
"""

import os
import re
import sqlite3
import sys

import requests


def main():
    """Call the rest of the functions--create db, scrape the text and send text to
    regex function.
    """
    create_db()
    text_ = scrape()
    process_scrape(text_)


def scrape():
    """Scrapes the AR page."""
    url = 'http://www.accuraterip.com/driveoffsets.htm'
    response = requests.get(url)
    return response.text


def process_scrape(text_):
    """Process the scrape and send offset values to add to database function."""
    regex = re.compile(r'<tr>\s+<td bgcolor="#(?:FCFCFC|F4F4F4)">'
                       r'<font face="Arial" size="2">(.*)</font></td>\s+'
                       r'<td align="center" bgcolor="#(?:FCFCFC|F4F4F4)">'
                       r'<font face="Arial" size="2">(.*)</font></td>')
    for match in regex.finditer(text_):
        if 'Purged' not in match.group(2):
            add_to_db(match.group(1), match.group(2))


def add_to_db(name, offset):
    """Adds an offset to the database."""
    query('INSERT INTO Drives (Name, Offset) VALUES (?, ?)', (name, offset))
    print('Added drive: {} (Offset: {}).'.format(name, offset))


def create_db():
    """Create the database."""
    query("""
        CREATE TABLE Drives (
            DriveID INTEGER NOT NULL PRIMARY KEY,
            Name TEXT NOT NULL,
            Offset TEXT NOT NULL
        )
    """)


def query(string, args=None):
    """Send a query to the DB."""
    path = os.path.join(sys.path[0], 'drives.db')
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    if args:
        cursor.execute(string, args)
    else:
        cursor.execute(string)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
