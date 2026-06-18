#!/usr/bin/env python3

"""Validate and filter YouTube IDs from stdin."""

import string
import sys
import logging

logging.basicConfig(filename = "pipeline_audit.log", level = logging.WARNING)

def youtube_id_validation(video_id):
    """Return True if video_id is a valid 11-char URL-safe Base64 string."""

    alphabets = string.ascii_letters
    digits = string.digits
    hyphen = "-"
    under_score = "_"

    valid_char_set = alphabets + digits + hyphen + under_score

    if len(video_id) != 11:
        logging.warning("invalid ID length: %s", video_id)
        return False

    for letter in video_id:
        if letter not in valid_char_set:
            logging.warning("invalid letters in ID entry: %s", video_id)
            return False

    return True

def main():
    """ Read IDs from stdin, print valid ones, log invalid ones. """
    try:
        for line in sys.stdin:
            # Strip newline characters and extra spaces
            clean_line = line.strip()

            # Skip empty lines
            if not clean_line:
                continue

            # If the line has an entry, validate the input
            if youtube_id_validation(clean_line):
                print(clean_line)

    except KeyboardInterrupt:
        print()
        sys.exit()

if __name__ == "__main__":
    main()
