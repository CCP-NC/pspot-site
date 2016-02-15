#!/usr/bin/env python

# Crude utility to turn CASTEP code excerpts into YAML library definitions

import sys
import re
import yaml

infile = open(sys.argv[1]).readlines()

lib = {}

librow_re = re.compile("\"([^\"]*)\"/ !\*[\s]+([A-Za-z]+)")

for l in infile:
    mtch = librow_re.findall(l)

    if len(mtch) > 0 and mtch[0][0] != '':
        lib[mtch[0][1]] = mtch[0][0]

print yaml.safe_dump(lib, default_flow_style=False)