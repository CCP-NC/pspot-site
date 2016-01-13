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
    try:
        castep_run = subprocess.Popen([config['castep_command'], '-dryrun', ppot.name], cwd=dirname)
        castep_run.wait()
    except OSError:
        sys.stderr.write("CASTEP run failed, skipping\n")
        return

def parse_agrfile(fname):

    # Parse a Grace file returning graphs, datasets for each of them, and additional info
    agrf = open(fname).readlines()
    agrobj = {}

    graphline_re = re.compile('@[gG]([0-9]+)[\s]+on')
    withline_re = re.compile('@with[\s]+[gG]([0-9]+)')
    propline_re = re.compile('@[\s]+([\w\s]+)[\s]+([\+\-0-9\.]+|"[^"]*"|off|on)')
    targline_re = re.compile('@target[\s]+[gG]([0-9]+)\.[sS]([0-9]+)')
    typeline_re = re.compile('@type[\s]+xy')
    dataline_re = re.compile('[\s]*([0-9eE\-\+\.]+)[\s]+([0-9eE\-\+\.]+)')

    current_with = None
    current_target = None

    for l in agrf:

        if current_with is not None:
            pm = propline_re.findall(l)
            if len(pm) != 1:
                current_with = None
                continue
            # Else, split the line into a series of properties in tree fashion
            prop_tree = ["with"] + pm[0][0].strip().split()
            prop_val = pm[0][1]
            def seq_tree_set(obj, tree, val):
                if len(tree) == 1:
                    obj[tree[0]] = val
                else:
                    if tree[0] not in obj:
                        obj[tree[0]] = {}
                    seq_tree_set(obj[tree[0]], tree[1:], val)
            seq_tree_set(agrobj[current_with], prop_tree, prop_val)
        elif current_target is not None:
            if typeline_re.match(l) is not None:
                continue
            dm = dataline_re.findall(l)
            if len(dm) != 1:
                current_target = None
                continue
            data = [float(d) for d in dm[0]]
            agrobj[current_target[0]]['sets'][current_target[1]].append(data)
        else:
            # Check if we have a graph, a with, or a target
            gm = graphline_re.findall(l)
            if len(gm) > 0:
                # Graph! Add it to the obj
                agrobj[int(gm[0])] = {'sets': {}, 'with': {}}
                continue
            wm = withline_re.findall(l)
            if len(wm) > 0:
                # With! Set the current_with, only if present
                if int(wm[0]) in agrobj:
                    current_with = int(wm[0])
                continue
            tm = targline_re.findall(l)
            if len(tm) > 0:
                # Target! Set the current_target, only if graph is present
                if int(tm[0][0]) in agrobj:
                    current_target = (int(tm[0][0]), int(tm[0][1]))
                    agrobj[current_target[0]]['sets'][current_target[1]] = []
                continue

    return agrobj

def parse_betaproj(ppot):

    global config, main_abspath

    # Go and fetch the beta projector file for the given pseudopotential

    dirname = os.path.join(main_abspath, config['graph_path'], ppot.name)
    beta_fname = os.path.join(dirname, ppot.name+'.beta')

    try:
        beta_obj = parse_agrfile(beta_fname)
    except IOError:
        sys.stderr.write("Could not parse beta projectors for pseudopotential {0}\n".format(ppot.name))
        return None

    return beta_obj

# Parsing command line arguments

parser = ap.ArgumentParser()
parser.add_argument('-noplot', action='store_true', default=False, help="Do not generate PSPOT plots")
parser.add_argument('-nocastep', action='store_true', default=False, help="Do not run CASTEP, use existing files if present")

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
    "cell_template": "template.cell",
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

pspot_file_list = glob.glob(os.path.join(main_abspath, config['pspot_path'], '*.' + config['pspot_extension']))
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

    if ppot.el not in pspot_info_dict:
        pspot_info_dict[ppot.el] = {'default': None}

    ppot_info = {'name': ppot.name,
                 'file': os.path.basename(fname),
                 'elem': ppot.el,
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

# Now save the entire dictionary as JSON
json.dump(pspot_info_dict, open(os.path.join(main_abspath, 'pspot_data.json'), 'w'), indent=2)

# Now generate the appropriate plots
if not args.noplot and cell_template is not None:

    if not args.nocastep:
        # Clear the folder
        clear_folder(os.path.join(main_abspath, config['graph_path']))

    agr_extensions = ['beta', 'econv', 'pwave']

    for p_i, ppot in enumerate(pspot_list):

        sys.stdout.write("Processing pseudopotential file {0} of {1}\n".format(p_i+1, len(pspot_list)))

        # Time to make graphs! First run CASTEP, then actually plot stuff

        if not args.nocastep:
            sys.stdout.write("Running CASTEP calculation\n")
            run_castep_calc(ppot)
        sys.stdout.write("Plotting graphs\n")
        dirname = os.path.join(main_abspath, config['graph_path'], ppot.name)

        for ext in agr_extensions:
            fname = os.path.join(dirname, ppot.el+'_OTF.'+ext)
            try:
                agr_obj = parse_agrfile(fname)
            except IOError:
                sys.stderr.write("Could not parse {0} file for pseudopotential {1}\n".format(ext, ppot.name))
                continue

            # Now dump it as json file
            json.dump(agr_obj, open(os.path.join(dirname, ext + '.json'), 'w'), indent=2)
            # Also create an SVG with Grace for good measure
            try:
                xmgrace_run = subprocess.Popen(['xmgrace', fname, '-hdevice', 
                                                'JPEG', '-hardcopy',
                                                '-printfile', os.path.join(dirname, ext+'.jpg'),
                                                '-fixed', '1024', '768'])
                xmgrace_run.wait()
            except OSError:
                sys.stderr.write("Grace not installed, PNG plots can not be generated\n")
