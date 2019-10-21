#!/usr/bin/env python

# Crude utility to turn CASTEP code excerpts into YAML library definitions

import sys
import re
import yaml
import argparse as ap

parser = ap.ArgumentParser(description='Read the CASTEP ion_atom_data.f90 file and return a YAML description of the libraries')
parser.add_argument('input_file', type=str, help='The file to parse')
parser.add_argument('-n', action='store_true', help='Whether to make the pseudopotential strings norm-conserving')

args = parser.parse_args()

infile = open(args.input_file).readlines()

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
        psstr = match_row[0][0]
        lib[header]['elements'][match_row[0][1]] = psstr



print(yaml.safe_dump(lib, default_style='"', default_flow_style=False))