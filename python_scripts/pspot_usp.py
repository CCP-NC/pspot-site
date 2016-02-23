# Definition of a class for parsing USP PSPOT files headers

import re
import os

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
			raise ValueError("PSPOT file {0} is not in correct USP format".format(fname))

		comment_block = lines[start_i+1:end_i]

		# Now grab the actually useful stuff
		self.cutoffs = {'COARSE': 0,
						'MEDIUM': 0,
						'FINE': 0,
						'EXTREME': 0}

		for c in self.cutoffs:
			cre = re.compile('([0-9\.]+)[\s]+'+c)
			for l in comment_block:
				res = cre.findall(l)
				if len(res) > 0:
					# Found it!
					try:
						self.cutoffs[c] = float(res[0])
					except ValueError:
						raise ValueError("PSPOT file {0} is corrupted".format(fname))
					break

		# Then find the element and the XC functional
		elre = re.compile("Element:[\s]+([A-Za-z]+) ")
		xcre = re.compile("Level of theory:[\s]+([A-Za-z]+) ")

		self.elem = None
		self.xc = None

		for l in comment_block:
			res = elre.findall(l)
			if len(res) > 0:
				self.elem = res[0]
				res = xcre.findall(l)
				if len(res) == 0:
					raise ValueError("PSPOT file {0} is corrupted".format(fname))
				self.xc = res[0]
				break

		if self.elem is None:
			raise ValueError("PSPOT file {0} is corrupted".format(fname))

		# Finally, the pseudpotential string. This is a bit harder to identify
		pspotsre = re.compile("\"([0-9a-zA-Z\.:|()=]+)(?:\[\])*\"")
		def is_dash(s):
			s = s.strip()
			return s == len(s)*'-'

		for i, l in enumerate(comment_block[1:-1]):
			# Is the block in between two dash-only lines?
			if is_dash(comment_block[i]) and is_dash(comment_block[i+2]):
				# Then we're onto something!
				res = pspotsre.findall(l)
				if len(res) == 0:
					raise ValueError("PSPOT file {0} is corrupted".format(fname))
				self.pspot_string = res[0]
				break

	def __dict__(self):

		return {'name': self.name,
                 'file': self.file,
                 'elem': self.elem,
                 'cutoffs': self.cutoffs,
                 'xc': self.xc,
                 'pspot_string': self.pspot_string}
