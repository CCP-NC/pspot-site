#!/usr/bin/env python
# A script postprocessing the PseudoPotential files to keep updated tables of their content

import re
import json
import sys
import os, glob
import yaml
import subprocess
import shutil
import argparse as ap

from pspot_usp import USPpspot


def clear_folder(fold):

    """ Delete all the contents of a given folder """

    for f in glob.glob(os.path.join(fold, '*')):
        try:
            shutil.rmtree(f)
        except OSError:
            try:
                os.remove(f)
            except OSError:
                sys.stderr.write("WARNING: couldn't delete {0}\n".format(f))

def lib_dirname(lib_name):

    """ Generate the name of the directory to hold the contents of a
        pseudopotential library. """

    global config, main_abspath

    return os.path.join(main_abspath, config['graph_path'], lib_name)

def pspot_dirname(pspot):

    global config, main_abspath

    return os.path.join(main_abspath, config['graph_path'], pspot.name)

def run_castep_calc(lib, lib_name):

    global config, main_abspath, cell_template, param_template

    # Generate the directory structure
    dirname = lib_dirname(lib_name)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    else:
        clear_folder(dirname)
        
    # A block process in order to be lighter on memory use when running CASTEP
    # Build the positions and pseudopotential blocks

    lib_blocks = [lib.items()[b_i:b_i+config['libblock_size']]
                  for b_i in range(0, len(lib), config['libblock_size'])]

    for bl in lib_blocks:

        positions_block = ''
        potentials_block = ''

        for el, pp in bl:
            if pp.endswith('[]'):
                pp = pp[:-2]
            positions_block += "{0} 0 0 0\n".format(el)
            potentials_block += "{0} {1}[]\n".format(el, pp)

        cell_file = cell_template.replace('<positions_block>', positions_block)
        cell_file = cell_file.replace('<potentials_block>', potentials_block)

        param_file = param_template # For now no replacement is needed


        cell_fname = os.path.join(dirname, lib_name+'.cell')
        open(cell_fname, 'w').write(cell_file)
        param_fname = os.path.join(dirname, lib_name+'.param')
        open(param_fname, 'w').write(param_file)

        # Now run a CASTEP dryrun
        try:
            castep_run = subprocess.Popen([config['castep_command'],
                                           '-dryrun',
                                           lib_name], cwd=dirname)
            castep_run.wait()
        except OSError:
            sys.stderr.write("CASTEP run failed, skipping\n")
            return

def run_gnuplot(pspot):

    global config, main_abspath, gp_template

    # Some useful shortcuts
    projs = pspot['PROJECTORS']
    rcs = [projs[p]['RC'] for p in projs]

    # Write the Gnuplot file for plotting
    gp_file = gp_template
    # Now run the necessary substitutions
    # First the potential name
    gp_file = gp_file.replace("<pspot.elem>", pspot['ELEMENT'])
    # The maximum X value
    gp_file = gp_file.replace("<x_max>", str(max(rcs)*1.2))
    # The local radius
    gp_file = gp_file.replace("<local_rc>", str(projs['LOC']['RC']))
    # Then the channel titles and plotting instructions for Beta projectors
    for i, ch in enumerate('spdf'):
        plot_string = ''
        scale_string = ''
        gp_file = gp_file.replace("<{0}_beta_title>".format(ch), ch + (" V_{local}" if i == projs['LOC']['L'] else ''))        
        if i < projs['LOC']['L']:
            # Add the arrow
            # Compile list of projectors
            beta_ch = sorted([p for p in projs if projs[p]['L'] == i]) # Ensure that they are in order (should be already warranted, but...)
            scale_string = '\n'.join(['set arrow from {0}, graph 0 to {0}, graph 1 nohead ls 0'.format(str(projs[b]['RC'])) for b in beta_ch])
            plot_string = ', "" '.join(["u 1:{0} w l ls {1} notitle".format(b+1, j+1) for j, b in enumerate(beta_ch)])
        elif i == projs['LOC']['L']:
            scale_string = 'stats "{0}_OTF.beta.dat" u {1} nooutput\n'.format(pspot['ELEMENT'], pspot['NUM_BETA']+3)
            scale_string += 'set yrange [(1.1*STATS_min < 0.9*STATS_min ? 1.1*STATS_min : 0.9*STATS_min) : 0.0]\n'
            scale_string += 'set arrow from {0}, graph 0 to {0}, graph 1 nohead ls 100'.format(str(projs['LOC']['RC']))
            plot_string = 'u 1:{0} w l ls 101 notitle, "" u 1:{1} w l ls 1 notitle'.format(pspot['NUM_BETA']+2, pspot['NUM_BETA']+3)
        else:
            plot_string = ' u 1:(0) w l ls 0 notitle'
        gp_file = gp_file.replace("<{0}_beta_scale>".format(ch), scale_string)
        gp_file = gp_file.replace("<{0}_beta_plot>".format(ch), plot_string)

    # Now for Pwave projectors
    for i, ch in enumerate('spdf'):
        plot_string = ''
        scale_string = ''
        gp_file = gp_file.replace("<{0}_pwave_title>".format(ch), ch + (" local" if i == projs['LOC']['L'] else ''))
        if i < projs['LOC']['L']:
            # Compile list of projectors
            beta_ch = sorted([p for p in projs if projs[p]['L'] == i]) # Ensure that they are in order (should be already warranted, but...)
            scale_string = '\n'.join(['set arrow from {0}, graph 0 to {0}, graph 1 nohead ls 0'.format(str(projs[b]['RC'])) for b in beta_ch])
            plot_string = ', "" '.join(['u 1:{0} w l ls {2} notitle, "" u 1:{1} w l ls {3} notitle'.format(2*b, 2*b+1, j+101, j+1) for j, b in enumerate(beta_ch)])
        elif i == projs['LOC']['L']:
            scale_string = 'set arrow from {0}, graph 0 to {0}, graph 1 nohead ls 0'.format(str(projs['LOC']['RC']))
            plot_string = 'u 1:{0} w l ls 1 notitle, "" u 1:{1} w l ls 101 notitle'.format(pspot['NUM_BETA']*2+2, pspot['NUM_BETA']*2+3)
        else:
            scale_string = 'set yrange [-1:0]'
            plot_string = ' u 1:(0) w l ls 0 notitle'

        gp_file = gp_file.replace("<{0}_pwave_scale>".format(ch), scale_string)
        gp_file = gp_file.replace("<{0}_pwave_plot>".format(ch), plot_string)


    gp_fname = os.path.join(main_abspath, pspot['basepath']+'.gp')
    open(gp_fname, 'w').write(gp_file)

    # Now run gnuplot
    dirname = lib_dirname(pspot['library'])
    try:
        gnuplot_run = subprocess.Popen([config['gnuplot_command'], gp_fname], cwd=dirname)
        gnuplot_run.wait()
    except OSError:
        sys.stderr.write("Gnuplot run failed, skipping plotting\n")
        return

def parse_agrfile(fname):

    # Parse a Grace file returning graphs, datasets for each of them, and additional info
    # CURRENTLY DEPRECATED AND NOT IN USE

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

def parse_betaproj(pspot):

    global config, main_abspath

    # Go and fetch the beta projector file for the given pseudopotential

    dirname = os.path.join(main_abspath, config['graph_path'], pspot.name)
    beta_fname = os.path.join(dirname, pspot.name+'.beta')

    try:
        beta_obj = parse_agrfile(beta_fname)
    except IOError:
        sys.stderr.write("Could not parse beta projectors for pseudopotential {0}\n".format(pspot.name))
        return None

    return beta_obj

# Parsing command line arguments

parser = ap.ArgumentParser()
parser.add_argument('-noplot', action='store_true', default=False, help="Do not generate PSPOT plots")
parser.add_argument('-nocastep', action='store_true', default=False, help="Do not run CASTEP, use existing files if present")
parser.add_argument('-only', type=str, nargs='+', default=None, help="Use only these libraries")

args = parser.parse_args()

# First some useful configurable constants
config = {
    "main_relpath": "..",
    "pspot_path": "data/libraries",
    "delta_path": "data/delta_test",
    "default_library": "test_library",
    "graph_path": "graphs",
    "castep_command": "castep.serial",
    "gnuplot_command": "gnuplot",
    "cell_template": "template.cell",
    "param_template": "template.param",
    "gp_template": "template.gp",
    "libblock_size": 20
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

# Load the template for cell & param files
cell_template = None
try:
    cell_template = open(config['cell_template']).read()
except IOError:
    sys.stderr.write("Cell template file not found, plots will not be produced\n")
param_template = None
try:
    param_template = open(config['param_template']).read()
except IOError:
    sys.stderr.write("Param template file not found, plots will not be produced\n")
gp_template = None
try:
    gp_template = open(config['gp_template']).read()
except IOError:
    sys.stderr.write("Gnuplot template file not found, plots will not be produced\n")

# Now load all the various libraries

if args.only is None:
    pspot_library_list = glob.glob(os.path.join(main_abspath, config['pspot_path'], '*'))
else:
    pspot_library_list = args.only
pspot_library_dict = {}
pspot_list = []

# Clear the folder containing the calculations
if not args.nocastep and cell_template is not None:
    # Ask for confirmation, this is some serious shit
    ans = raw_input("To run the calculations the entire content of graph_path will be deleted, continue [y/N]?")
    if ans.lower() != 'y':
        sys.exit("Execution interrupted")
    clear_folder(os.path.join(main_abspath, config['graph_path']))

for lib_fname in pspot_library_list:
    
    # Parse the given library
    try:
        lib = yaml.load(open(lib_fname))
    except yaml.scanner.ScannerError as e:
        sys.stderr.write("Parsing of library {0} failed.\nDetails: {1}\n" +
                         "Skipping...\n".format(lib_fname, e))
        continue

    lib_name = os.path.splitext(os.path.basename(lib_fname))[0] # Remove the extension if present
    if lib_name not in pspot_library_dict:
        pspot_library_dict[lib_name] = lib
    else:
        sys.stderr.write("Duplicated library with name {0} detected.\n" +
                         "Skipping...".format(lib_name))

    # "Default" is specially reserved
    if lib_name == "default":
        sys.stderr.write("The name 'default' is reserved and can not be " +
                         "used for a pseudopotential library. Skipping...\n")
        continue

    # Now run a CASTEP calculation on the whole library (if so requested)
    if not args.nocastep and cell_template is not None:
        sys.stdout.write("Running CASTEP calculation" +
                         " for library {0}\n".format(lib_name))
        run_castep_calc(lib, lib_name)

# Now save the related info in full form,
# split BY ELEMENT rather than by library
pspot_elem_dict = {}

for lib_name in pspot_library_dict:

    lib = pspot_library_dict[lib_name]
    libdir = lib_dirname(lib_name)

    # Also open the delta test info if present
    try:
        delta_info = yaml.safe_load(open(os.path.join(main_abspath, config['delta_path'], lib_name + "_delta.yml")))
    except IOError:
        delta_info = None

    for el in lib:
        
        # Load the info file for all useful values
        el_fname = os.path.join(libdir, '{0}_OTF.info.yml'.format(el))
        try:
            pspot = yaml.safe_load(open(el_fname))
        except (IOError, yaml.error.MarkedYAMLError) as e:
            # Something didn't work, skip
            sys.stderr.write("Parsing of file {0} failed.\nDetails: {1}\nSkipping...\n".format(el_fname, e))
            continue

        # This horribly hackish solution offered you by PyYAML being not only dumb enough to decide that the string "No" is actually
        # a Boolean meaning False rather than the chemical symbol of Nobelium, but also inconsistent enough that apparently the version
        # I have installed on my office computer can't even tell when the string is surrounded by effin' QUOTES!
        # Of course I could just update it but never know when, where and by whom this is going to be ran in the future, 
        # so better safe than sorry... I don't think any element with chemical symbol "Yes" is going to be relevant in the close future
        # anyway.
        if type(pspot['ELEMENT']) is bool:
            pspot['ELEMENT'] = "No"

        if el not in pspot_elem_dict:
            pspot_elem_dict[el] = {'default': None}

        pspot_elem_dict[el][lib_name] = pspot
        # Add some information
        pspot_elem_dict[el][lib_name]['library'] = lib_name
        pspot_elem_dict[el][lib_name]['pspot_string'] = lib[el]
        # This one forms the basis for all related files (plots etc.)
        # with different terminations/extensions
        pspot_elem_dict[el][lib_name]['basepath'] = os.path.join(config['graph_path'], lib_name, el)
        if delta_info is not None and el in delta_info:
            pspot_elem_dict[el][lib_name]['delta_info'] = delta_info[el]
        else:
            pspot_elem_dict[el][lib_name]['delta_info'] = []            

        if lib_name == config['default_library']:
            pspot_elem_dict[el]['default'] = pspot_elem_dict[el][lib_name]

# Now save the entire dictionary as JSON
json.dump(pspot_elem_dict, open(os.path.join(main_abspath, 'pspot_data.json'), 'w'), indent=2)

# Now generate the appropriate plots
if not args.noplot:

    agr_extensions = ['beta', 'econv', 'pwave']

    for el in pspot_elem_dict:
        for lib in pspot_elem_dict[el]:

            if lib == 'default':
                # Skip or it will be duplicated
                continue

            sys.stdout.write(("Processing pseudopotential file: {0}," +
                              " library: {1}\n").format(el, lib))

            # Time to make graphs! First run CASTEP, then actually plot stuff

            sys.stdout.write("Plotting graphs\n")

            run_gnuplot(pspot_elem_dict[el][lib])
