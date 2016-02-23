#!/usr/bin/env python

# Very simple utility to read the output of a delta test file and dump it as a YAML file

import sys
import yaml

ifile = open(sys.argv[1])

deltadat = {}

for l in ifile.readlines():

	# Discard the line if it begins with anything but a capital letter
	if not l[0].isupper():
		continue

	# Else, parse it
	lsplit = l.split()

	if len(lsplit) < 4:
		continue

	deltadat[lsplit[0]] = [float(x) for x in lsplit[1:4]]


print yaml.safe_dump(deltadat)