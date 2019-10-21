#!/usr/bin/env python

import os
import re
import sys
import yaml
import glob
import shutil
import argparse as ap
import subprocess as sp
from ase import io, Atoms
from ase.calculators.castep import create_castep_keywords, Castep

parser = ap.ArgumentParser(
    description='Script to automatically generate pseudopotential files and '
    'data from a library of strings and a CASTEP installation')

parser.add_argument('yaml_file', type=str,
                    help='YAML library with pseudopotential strings')
parser.add_argument('-cbin', type=str, default='castep.serial',
                    help='Path to CASTEP binary')
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


args = parser.parse_args()

pspotlibs = yaml.safe_load(open(args.yaml_file))

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
            print('Library: {0}, Elements: {1}'.format(lib, seed))
            proc = sp.Popen([args.cbin, '--dryrun', seed], cwd=libdir, 
                stdout=sp.PIPE, stderr=sp.PIPE)
            out, err = proc.communicate()

print(pspotcalc)

if args.tclean:
    shutil.rmtree(os.path.join(abspath, args.tdir))
