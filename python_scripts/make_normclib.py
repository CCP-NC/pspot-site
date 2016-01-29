# A very basic script to turn any library into a norm conserving version of itself

import re
import sys
import yaml

# Library file is first command line argument

lib = yaml.safe_load(open(sys.argv[1]))

# Now fix the various strings

for el in lib:
	split_string = lib[el].split('|')
	string_end = split_string[-1].split('(')
	projs = string_end[0].split(':')
	# Now rebuild
	string_end[0] = ':'.join([p + 'N' for p in projs])
	split_string[-1] = '('.join(string_end)
	lib[el] = '|'.join(split_string)

print yaml.safe_dump(lib, default_flow_style=False)
