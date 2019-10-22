# Definition of a class for parsing USP PSPOT files headers

import re
import os
import scipy.constants as cnst

_Ha2eV = cnst.physical_constants['Hartree energy in eV'][0]
_au2Ang = cnst.physical_constants['Bohr radius'][0]*1e10

class USPpspot(object):

    def __init__(self, fname):
        """ Initialize the object

        fname [string] - path to the file containing the pseudopotential

        """

        f = open(fname)
        lines = f.readlines()

        self.file = os.path.basename(fname)
        self.name = os.path.splitext(self.file)[0]

        try:
            start_i = lines.index("START COMMENT\n")
            end_i = lines.index("END COMMENT\n")
        except ValueError:
            raise ValueError(
                "PSPOT file {0} is not in correct USP format".format(fname))

        comment_block = lines[start_i+1:end_i]

        # Now grab the actually useful stuff
        self.cutoffs = {'COARSE': None,
                        'MEDIUM': None,
                        'FINE': None,
                        'EXTREME': None}

        # Cutoffs
        cre = re.compile('([0-9\\.]+)\\s+(COARSE|MEDIUM|FINE|EXTREME)')

        # Element, XC functional, ionic charge
        elre = re.compile("Element:\\s+([A-Za-z]+) ")
        icre = re.compile("Ionic charge:\\s+([0-9.]+) ")
        xcre = re.compile("Level of theory:\\s+([A-Za-z0-9\\-]+) ")
        solre = re.compile("Atomic Solver:\\s+([A-Za-z0-9\\-]+) ")

        # Finally, the pseudpotential string. This is a bit harder to identify
        pspotsre = re.compile("\"([0-9a-zA-Z.,:|()=+\-{}]+)(?:\[.*\])*\"")        

        for i, l in enumerate(comment_block):
            # Identify cutoffs
            cuts = cre.findall(l)
            if len(cuts) > 0:
                x, c = cuts[0]
                self.cutoffs[c] = float(x)

            el = elre.findall(l)
            if len(el) > 0:
                self.elem = el[0]

            ic = icre.findall(l)
            if len(ic) > 0:
                self.ion_charge = float(ic[0])

            xc = xcre.findall(l)
            if len(xc) > 0:
                self.xc = xc[0]

            sol = solre.findall(l)
            if len(sol) > 0:
                self.sol = sol[0]

            # Pseudopotential strings can go to the next line!
            qc = l.count('"')
            if qc == 2:
                psstr = pspotsre.findall(l)
                if len(psstr) > 0:
                    self.pspot_string = psstr[0]
            elif qc == 1 and not hasattr(self, 'pspot_string'):
                psstr = (l.rsplit('|', 1)[0].strip() + 
                         comment_block[i+1].split('|', 1)[1].strip())
                psstr = pspotsre.findall(psstr)
                if len(psstr) > 0:
                    self.pspot_string = psstr[0]                

            # Match the more complex stuff
            if 'Reference Electronic Structure' in l:
                self.elec_struct = []
                for l2 in comment_block[i+2:]:
                    lspl = l2.split()
                    if len(lspl) < 5:
                        break

                    self.elec_struct.append({'orbital': lspl[1],
                                             'occupancy': float(lspl[2]),
                                             'energy': float(lspl[3])*_Ha2eV})

            if 'Pseudopotential Definition' in l:
                self.pspot_def = []
                for l2 in comment_block[i+2:]:
                    lspl = l2.split()
                    if len(lspl) < 8:
                        break 

                    self.pspot_def.append({'beta': lspl[1],
                                           'l': 'spdfghi'[int(lspl[2])],
                                           'energy': float(lspl[3])*_Ha2eV,
                                           'Rc': float(lspl[4])*_au2Ang,
                                           'scheme': lspl[5],
                                           'norm': float(lspl[6])})

        # Test
        try:
            self.__dict__()
        except AttributeError:
            raise ValueError(
                "PSPOT file {0} is not in correct USP format".format(fname))


    def __dict__(self):

        return {'name': self.name,
                'file': self.file,
                'elem': self.elem,
                'ionic_charge': self.ion_charge,
                'cutoffs': self.cutoffs,
                'xc': self.xc,
                'solver': self.sol,
                'electronic_structure': self.elec_struct,
                'pseudopotential_definition': self.pspot_def,
                'pspot_string': self.pspot_string}


if __name__ == "__main__":

    import sys

    ps = USPpspot(sys.argv[1])
    print(ps.__dict__())
