# A script postprocessing the PseudoPotential files to keep updated tables of their content

import json
import sys
import os, glob
import yaml

from pspot_usp import USPppot

# First some useful configurable constants
config = {
	"main_relpath": "..",
	"pspot_path": "data/pspot",
	"pspot_extension": "usp",
	"pspot_name_separator": "_",
	"pspot_default_termination": "OTF",
	"graph_paht": "graphs",
	"castep_command": "castep.serial",
	"cell_template": "template.cell"
} # Default settings

# Overridde by config file
config.update(yaml.safe_load(open('pspot_process_config.yml')))

# Load the template for cell files
cell_template = None
try:
	cell_template = open(config['cell_template']).read()
except IOError:
	sys.stderr.write("Cell template file not found, plots will not be produced")

# Now start by building a full table of all pseudopotential files

pspot_file_list = glob.glob(os.path.join(config['main_relpath'], config['pspot_path'], '*.' + config['pspot_extension']))
pspot_list = {}

for fname in pspot_file_list:

	# Parse assuming USP format
	# If not valid, just skip
	try:
		ppot = USPppot(fname)
	except (IOError, ValueError) as e:
		# Something didn't work, skip
		sys.stderr.write("Parsing of file {0} failed.\nDetails: {1}\nSkipping...\n".format(fname, e))
		continue

	# Now assign
	ppname = os.path.splitext(os.path.basename(fname))[0]
	# "Default" is specially reserved
	if ppname == "default":
		sys.stderr.write("The name 'default' is reserved and can not be used for a pseudopotential file. Skipping...\n")
		continue

	if ppot.el not in pspot_list:
		pspot_list[ppot.el] = {'default': None}

	ppot_info = {'name': ppname,
 			     'path': os.path.join(config['pspot_path'], os.path.basename(fname)),
 			     'cutoffs': ppot.cutoffs,
 			     'xc': ppot.xc,
 			     'ppot_string': ppot.pspots}

	pspot_list[ppot.el][ppname] = ppot_info

	# And if default tag it as such
	is_default = (ppname.split(config['pspot_name_separator'])[-1] == config['pspot_default_termination'])
	if is_default:
		pspot_list[ppot.el]['default'] = ppot_info

	# Now generate the appropriate plots
	if cell_template is not None:

		cell_file = cell_template.replace('<symbol>', ppot.el)
		cell_file = cell_file.replace('<pspot_string>', ppot.pspots)

		# Save it
		
