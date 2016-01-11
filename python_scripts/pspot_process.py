# A script postprocessing the PseudoPotential files to keep updated tables of their content

import re
import json
import sys
import os, glob
import yaml
import subprocess
import shutil
import argparse as ap

from pspot_usp import USPppot

def clear_folder(fold):

    # Grab everything in the folder and delete it
    for f in glob.glob(os.path.join(fold, '*')):
        try:
            shutil.rmtree(f)
        except OSError:
            try:
                os.remove(f)
            except OSError:
                sys.stderr.write("WARNING: couldn't delete {0}\n".format(f))

def run_castep_calc(ppot):

    global config, main_abspath

    cell_file = cell_template.replace('<symbol>', ppot.el)
    cell_file = cell_file.replace('<pspot_string>', ppot.pspots)

    # Save it in its own folder
    dirname = os.path.join(main_abspath, config['graph_path'], ppot.name)
    os.mkdir(dirname)
    cell_fname = os.path.join(dirname, ppot.name+'.cell')
    open(cell_fname, 'w').write(cell_file)

    # Now run a CASTEP dryrun
    castep_run = subprocess.Popen([config['castep_command'], '-dryrun', ppot.name], cwd=dirname)
    castep_run.wait()

def parse_betaproj(ppot):

    global config, main_abspath

    # Go and fetch the beta projector file for the given pseudopotential

    dirname = os.path.join(main_abspath, config['graph_path'], ppot.name)
    beta_fname = os.path.join(dirname, ppot.name+'.beta')

    try:
        beta_lines = open(beta_fname).readlines()
    except IOError:
        sys.stderr.write("Could not parse beta projectors for pseudopotential {0}\n".format(ppot.name))
        return None

    beta_proj = {}

    # First identify how many projectors are defined and where
    on_re = re.compile("@g([0-9]+)[\s]+on")

    for l in beta_lines:
        on_match = on_re.findall(l)
        if len(on_match) > 0:
            print on_match


# Parsing command line arguments

parser = ap.ArgumentParser()
parser.add_argument('-plot', action='store_true', default=True, help="Run castep and generate PSPOT plots")

args = parser.parse_args()

# First some useful configurable constants
config = {
    "main_relpath": "..",
    "pspot_path": "data/pspot",
    "pspot_extension": "usp",
    "pspot_name_separator": "_",
    "pspot_default_termination": "OTF",
    "graph_path": "graphs",
    "castep_command": "castep.serial",
    "cell_template": "template.cell"
} # Default settings

# The directory of the project, calculated relative to the physical location of the script
main_abspath = os.path.join(sys.path[0], config['main_relpath']) 

# Overridde by config file
try:
    config.update(yaml.safe_load(open('pspot_process_config.yml')))
except IOError:
    # No config file? Eh, no problem. Use defaults and create it
    yaml.safe_dump(config, open('pspot_process_config.yml', 'w'))
    pass

# Load the template for cell files
cell_template = None
try:
    cell_template = open(config['cell_template']).read()
except IOError:
    sys.stderr.write("Cell template file not found, plots will not be produced\n")

# Now start by building a full table of all pseudopotential files

pspot_file_list = glob.glob(os.path.join(config['main_relpath'], config['pspot_path'], '*.' + config['pspot_extension']))
pspot_list = []
pspot_info_dict = {}

for f_i, fname in enumerate(pspot_file_list):
    
    # Parse assuming USP format
    # If not valid, just skip
    try:
        ppot = USPppot(fname)
    except (IOError, ValueError) as e:
        # Something didn't work, skip
        sys.stderr.write("Parsing of file {0} failed.\nDetails: {1}\nSkipping...\n".format(fname, e))
        continue

    # "Default" is specially reserved
    if ppot.name == "default":
        sys.stderr.write("The name 'default' is reserved and can not be used for a pseudopotential file. Skipping...\n")
        continue

    if ppot.el not in pspot_list:
        pspot_info_dict[ppot.el] = {'default': None}

    ppot_info = {'name': ppot.name,
                 'path': os.path.join(config['pspot_path'], os.path.basename(fname)),
                 'cutoffs': ppot.cutoffs,
                 'xc': ppot.xc,
                 'ppot_string': ppot.pspots}

    pspot_info_dict[ppot.el][ppot.name] = ppot_info

    # And if default tag it as such
    is_default = (ppot.name.split(config['pspot_name_separator'])[-1] == config['pspot_default_termination'])
    if is_default:
        pspot_info_dict[ppot.el]['default'] = ppot_info

    pspot_list.append(ppot)

# Now generate the appropriate plots
if args.plot and cell_template is not None:

    # Clear the folder
    clear_folder(os.path.join(main_abspath, config['graph_path']))

    for p_i, ppot in enumerate(pspot_list):

        sys.stdout.write("Processing pseudopotential file {0} of {1}\n".format(p_i+1, len(pspot_list)))

        # Time to make graphs! First run CASTEP, then actually plot stuff

        sys.stdout.write("Running CASTEP calculation\n")
        run_castep_calc(ppot)
        sys.stdout.write("Plotting graphs\n")
        parse_betaproj(ppot)
