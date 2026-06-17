#!/usr/bin/env python3

import string
import sys
import logging

logging.basicConfig(filename = "pipeline_audit.log", level = logging.WARNING)

def  youtube_id_validation(id):
	alphabets = string.ascii_letters
	digits = string.digits
	hyphen = "-"
	under_score = "_"

	valid_char_set = alphabets + digits + hyphen + under_score

	if len(id) != 11:
		logging.warning(f"invalid ID length. {id}")
		return False
	else:
		for letter in id:
			if letter not in valid_char_set:
				logging.warning(f"invalid letters in ID entry: {id}")
				return False
	return True


def main():
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

if __name__ == "__name__":
	main()
