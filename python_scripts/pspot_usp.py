# A class to parse USP pseudopotentials

import re
import os

class USPppot:

    def __init__(self, fname):

        # Load the file
        f = open(fname).read()

        # Pick comment block
        try:
            start_i = f.index("START COMMENT")
            end_i = f.index("END COMMENT")
        except ValueError:
            raise ValueError("File {0} is not in correct USP format or "
                             "is corrupted".format(fname))

        comment_block = f[start_i:end_i].split('\n')[1:]

        # Now to parse stuff
        self.cutoffs = {}
        self.el = None
        self.xc = None
        self.pspots = None

        # Regular expressions
        cut_re = re.compile("([0-9\.]+)[\s]+(COARSE|MEDIUM|FINE|EXTREME)")
        elxc_re = re.compile("Element:[\s]+([A-Za-z]+)[\s]+Ionic charge:[\s]+[0-9\.]+[\s]+Level of theory:[\s]+([A-Za-z0-9]+)")
        def is_dashline(s):
            s = s.strip()
            return s == len(s)*'-'
        pspots_re = re.compile("\"([|0-9A-Za-z\.:()=]+)\"")

        for l_i, l in enumerate(comment_block):

            cut_match = cut_re.findall(l)
            for m in cut_match:
                try:
                    self.cutoffs[m[1]] = float(m[0])
                except ValueError:
                    raise ValueError("File {0} is not in correct USP format "
                                     "or is corrupted".format(fname))

            if self.el is None:
                elxc_match = elxc_re.findall(l)
                if len(elxc_match) > 0:
                    self.el = elxc_match[0][0]
                    self.xc = elxc_match[0][1]

            if self.pspots is None and l_i < len(comment_block)-2:
                if is_dashline(l) and is_dashline(comment_block[l_i+2]):
                    # Then the next one might be it
                    pspots_match = pspots_re.findall(comment_block[l_i+1])
                    if len(pspots_match) > 0:
                        self.pspots = pspots_match[0]

        if self.el is None or self.pspots is None:
            raise ValueError("File {0} is not in correct USP format "
                             "or is corrupted".format(fname))
            






