#!/usr/bin/env python

import os
import re
import sys
import yaml
import glob
import json
import shutil
import argparse as ap
import subprocess as sp
from pspot_usp import USPpspot
from ase import io, Atoms
from ase.calculators.castep import create_castep_keywords, Castep

parser = ap.ArgumentParser(
    description='Script to automatically generate pseudopotential files and '
    'data from a library of strings and a CASTEP installation')

parser.add_argument('yaml_file', type=str,
                    help='YAML library with pseudopotential strings')
parser.add_argument('-cbin', type=str, default='castep.serial',
                    help='Command to run CASTEP binary')
parser.add_argument('-n', type=int, default=10,
                    help='Elements generated per file')
parser.add_argument('-tdir', type=str, default='.castep-temp',
                    help='Temporary directory to store the files')
parser.add_argument('-tclean', action='store_true', default=False,
                    help='Delete the temporary directory when finished')
parser.add_argument('-ckeyw', action='store_true', default=False,
                    help='If true, regenerate the ASE castep_keywords file')
parser.add_argument('-reuse', action='store_true', default=True,
                    help='If true, reuse any found pseudopotential files')
parser.add_argument('-nocalc', action='store_true', default=False,
                    help='If true, skip running CASTEP calculations')
parser.add_argument('-grbin', type=str, default='xmgrace',
                    help='Command to run xmgrace binary')
parser.add_argument('-graphs', type=str, default='graphs',
                    help='Folder to save graphs')
parser.add_argument('-deflib', type=str, default=None,
                    help='Default library (when present)')


args = parser.parse_args()

pspotlibs = yaml.safe_load(open(args.yaml_file))

# Find default library
if args.deflib is None:
    v = 0
    lre = re.compile('C([0-9]+)')
    for l in pspotlibs:
        m = lre.match(l)
        if m is not None:
            v = max(v, int(m.groups()[0]))
    deflib = 'C{0}'.format(v)
else:
    deflib = args.deflib

if args.ckeyw:
    create_castep_keywords(castep_command=args.cbin)

abspath = os.path.split(os.path.abspath(__file__))[0]

try:
    os.mkdir(os.path.join(abspath, args.tdir))
except FileExistsError:
    pass

pspotcalc = {}

for lib, libdata in pspotlibs.items():
    # Elements and strings
    psstr = [(e, p) for e, p in libdata['elements'].items() if p != '']
    # Create a temporary directory
    libdir = os.path.join(abspath, args.tdir, lib)
    try:
        os.mkdir(libdir)
    except FileExistsError:
        pass

    pspotcalc[lib] = {'description': libdata['description'],
                      'libdir': libdir,
                      'elements': []}

    # Find any already solved pseudopotentials
    lfiles = glob.glob(os.path.join(libdir, '*'))
    complete = []
    for el in list(zip(*psstr))[0]:
        exists = True
        for ext in ['usp', 'beta', 'econv', 'pwave']:
            fl = glob.glob(os.path.join(libdir, '{0}_*.{1}'.format(el, ext)))
            exists = exists and len(fl) == 1
        if exists:
            complete.append(el)
    psstr = [(e, p) for e, p in psstr if e not in complete]

    pspotcalc[lib]['elements'] += complete

    # Remove all existing cell files
    for f in glob.glob(os.path.join(libdir, '*.cell')):
        os.remove(f)

    for i in range(0, len(psstr), args.n):
        block = [(e, s + ('' if s[-2:] == '[]' else '[]'))
                 for e, s in psstr[i:i+args.n]]
        elems = list(zip(*block))[0]
        a = Atoms(elems, cell=[1, 1, 1])
        calc = Castep(castep_command=args.cbin)
        calc.cell.species_pot = block
        a.set_calculator(calc)

        seed = '{0}-{1}'.format(elems[0], elems[-1])
        io.write(os.path.join(libdir, seed + '.cell'), a)

        # Run calculation
        if not args.nocalc:
            print(
                'Calculation - Library: {0}, Elements: {1}'.format(lib, seed))
            proc = sp.Popen([args.cbin, '--dryrun', seed], cwd=libdir,
                            stdout=sp.PIPE, stderr=sp.PIPE)
            out, err = proc.communicate()


unique_elements = set.union(*[set(v['elements'])
                              for v in pspotcalc.values()])
element_data = {el: {'deflib': deflib} for el in unique_elements}
element_data['descriptions'] = {}

for lib, libdata in pspotcalc.items():
    libdir = libdata['libdir']
    element_data['descriptions'][lib] = libdata['description']
    # Read data from USP files
    for el in libdata['elements']:
        print('Graph plotting - Library: {0}, Element: {1}'.format(lib, el))
        try:
            uspf = glob.glob(os.path.join(libdir, '{0}_*.usp'.format(el)))[0]
            usp = USPpspot(uspf)
        except IndexError:
            raise RuntimeError('USP file for {0}:{1} not found'.format(lib,
                                                                       el))

        data = usp.__dict__()

        # Now plot the graphs
        betain = uspf.replace('usp', 'beta')
        betaout = os.path.join(args.graphs,
                               '{0}_{1}_beta.png'.format(lib, el))
        proc = sp.Popen([args.grbin, '-nxy', betain, '-hdevice', 'PNG',
                         '-hardcopy', '-printfile',
                         os.path.join(abspath, '..', betaout)],
                        stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = proc.communicate()

        data['beta_png'] = betaout

        econvin = uspf.replace('usp', 'econv')
        econvout = os.path.join(args.graphs,
                               '{0}_{1}_econv.png'.format(lib, el))
        proc = sp.Popen([args.grbin, '-nxy', econvin, '-hdevice', 'PNG',
                         '-hardcopy', '-printfile',
                         os.path.join(abspath, '..', econvout)],
                        stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = proc.communicate()

        data['econv_png'] = econvout

        pwavein = uspf.replace('usp', 'pwave')
        pwaveout = os.path.join(args.graphs,
                               '{0}_{1}_pwave.png'.format(lib, el))
        proc = sp.Popen([args.grbin, '-nxy', pwavein, '-hdevice', 'PNG',
                         '-hardcopy', '-printfile',
                         os.path.join(abspath, '..', pwaveout)],
                        stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = proc.communicate()

        data['pwave_png'] = pwaveout
        
        element_data[el][lib] = data

json.dump(element_data, open('../pspot_data_new.json', 'w'), indent=2)

# if args.tclean:
#     shutil.rmtree(os.path.join(abspath, args.tdir))
