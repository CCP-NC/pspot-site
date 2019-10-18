#!/usr/bin/env python

# Crude utility to turn CASTEP code excerpts into YAML library definitions

import sys
import re
import yaml

infile = open(sys.argv[1]).readlines()

lib = {}
libdesc_re = re.compile("ps_set = ([0-9]+)\s+->(.+)")
libhead_re = re.compile("ps_lib[\(\),0-9\s]+/\"([a-zA-Z0-9]+)\"")
librow_re = re.compile("ps_def[\(\),0-9\s]+/\"([^\"]*)\"/ !\*[\s]+([A-Za-z]+)")

header = None
desc = ''

for l in infile:
	match_desc = libdesc_re.findall(l)
	match_head = libhead_re.findall(l)
	match_row = librow_re.findall(l)

	if len(match_desc) > 0:
		desc = match_desc[0][1].strip()

	if len(match_head) > 0:
		header = match_head[0]
		lib[header] = {'description': desc, 'elements': {}}

	if header is not None and len(match_row) > 0:
		lib[header]['elements'][match_row[0][1]] = match_row[0][0]

print(yaml.safe_dump(lib, default_flow_style=False))