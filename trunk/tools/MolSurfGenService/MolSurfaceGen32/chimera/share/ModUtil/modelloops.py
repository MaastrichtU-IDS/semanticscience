# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter as Tk

import chimera
from chimera.baseDialog import ModelessDialog

_singleton = None
def gui():
	global _singleton
	if not  _singleton:
		_singleton = Interface()
	_singleton.enter()

class Interface(ModelessDialog):

	title = "Model Loops with Modeller"
	buttons = ("OK", "Cancel")
	help = "ContributedSoftware/model/model.html"

	def __init__(self, *args, **kw):
		ModelessDialog.__init__(self, *args, **kw)
		# TODO: initialize instance variables

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeOptionMenu
		from chimera.tkoptions import IntOption, BooleanOption, \
				InputFileOption, StringOption, EnumOption
		import itertools
		info = Tk.Label(parent, justify=Tk.LEFT, wraplength=300, text=
				"Model alternate conformations of loops using "
				"Modeller from <http://salilab.org/>.\n"
				"First select the loops you wish to model."
				"  Then choose the number of models "
				"you wish to generate.")
		info.pack(ipadx=2, ipady=2)
		options = Tk.Frame(parent)
		options.columnconfigure(0, pad=2)
		options.columnconfigure(1, pad=2)
		row = itertools.count()
		molRow = row.next()
		text = Tk.Label(options,
				text="Restrict selections to molecule:")
		text.grid(row=molRow, column=0)
		self.molecules = MoleculeOptionMenu(options)
		self.molecules.grid(row=molRow, column=1, sticky=Tk.W)
		self.turnsOnly = BooleanOption(options, row.next(),
				"Restrict selections to turns", True, None)
		self.hetatms = BooleanOption(options, row.next(),
				"Include HETATM residues", False, None)
		self.waters = BooleanOption(options, row.next(),
				"Include waters", False, None)
		self.waters.disable()
		self.nucleic = BooleanOption(options, row.next(),
				"Include nucleic acids", False, None)
		self.nucleic.disable()
		self.count = IntOption(options, row.next(), "Number of models",
				10, None, min=1, sticky=Tk.W)
		#self.start = IntOption(options, row.next(),
		#		"Starting model number", 1, None, min=0)
		class Refinement(EnumOption):
			values = ('very fast', 'fast', 'slow', 'very slow',
				'slow large', 'none')
		self.refine = Refinement(options, row.next(), "Refinement",
								'fast', None)
		button = Tk.Button(options, text="Prune selection",
				command=self.prune)
		button.grid(row=row.next(), column=0, columnspan=2, pady=2)
		self.start = 1
		hr = Tk.Frame(options, relief=Tk.GROOVE, borderwidth=1, height=2)
		hr.grid(row=row.next(), columnspan=2, sticky='ew')
		# modeller location
		self.modeller = InputFileOption(options, row.next(),
				"Modeller location", "mod9v2", None)
		# temporary prefix -- TODO: add unique id
		#self.tempdir = StringOption(options, row.next(),
		#		"Temporary file prefix", "modtmp", None)
		options.pack()

	def prune(self):
		from chimera import selection
		molecule = self.molecules.getvalue()
		import ModUtil
		pairs, residues = ModUtil.convertSelection(
				selection._currentSelection,
				minLen=4, molecule=molecule,
				keepHet=self.hetatms.get(),
				keepNA=self.nucleic.get(),
				turnsOnly=self.turnsOnly.get())
		sel = selection.ItemizedSelection()
		sel.add(residues)
		sel.addImplied()
		selection.mergeCurrent(selection.INTERSECT, sel)
		return pairs, residues

	def Apply(self):
		pairs, residues = self.prune()
		if not pairs:
			from chimera import replyobj
			replyobj.status("no residues meet loop modelling criteria")
			return

		# create a temporary directory to work in
		import tempfile
		tempdir = tempfile.mkdtemp(prefix="modeller")
		print 'Modeller temporary directory:', tempdir

		# write PDB file with original coordinates
		import os
		fname = os.path.join(tempdir, 'original.pdb')
		molecule = self.molecules.getvalue()
		xform = molecule.openState.xform
		xform.invert()	# want original coordinates
		chimera.viewer.pdbWrite([molecule], xform, fname)
		# write out Modeller input file
		count = self.count.get()
		refine = self.refine.get()
		fname = os.path.join(tempdir, "loopopt.py")
		f = file(fname, 'w')
		writeModeller(f, 'original.pdb', 'loop', pairs, count, refine)
		f.close()

		#  run Modeller -- put up progress dialog
		import ModUtil
		def cb(process, dirname=tempdir, count=count):
			return loopFileCount(dirname, count)
		try:
			prog = self.modeller.get()
			p = ModUtil.run([prog, "loopopt.py"], cb, cwd=tempdir)
		except OSError, e:
			from chimera import replyobj
			replyobj.error("Unable to run modeller: %s\n" % e)
			return

		# Do concurrent work here

		# find atoms that are connected to the residues we will model
		atoms = set()
		for r in residues:
			for a in r.atoms:
				atoms.add(a)
		outsideAtoms = set()
		for a in atoms:
			for b in a.bonds:
				oa = b.otherAtom(a)
				if oa.residue not in residues:
					outsideAtoms.add(oa)
		outsideAtoms = [(a.residue.id, a.name) for a in outsideAtoms]

		residueIds = set([r.id for r in residues])

		# TODO: use triggers to monitor process
		# and then startup dock interface
		# For now, we just wait
		returncode = p.wait()
		if returncode != 0:
			from chimera import replyobj
			replyobj.error("Modeller failed\n")
			return

		# create ViewDock input file from output files
		path = makedock(tempdir, residueIds, outsideAtoms)
		if not path:
			from chimera import replyobj
			replyobj.error("No models were generated\n")
			return

		# undisplay selected residues
		for r in residues:
			for a in r.atoms:
				a.display = False

		# startup dock
		import ViewDock
		v = ViewDock.ViewDock(path, 'Modeller')

		# remove long bonds since makedock can't put TERs
		# from both the model and the "longbond" PseudoBondGroup
		models = [c.chimeraModel for c in v.results.compoundList]
		length = 3
		sqLen = length * length
		for m in models:
			for b in m.bonds:
				if b.sqlength() >= sqLen:
					# get rid of longbond PseudoBonds
					a0, a1 = b.atoms
					pbs = a0.associations(
						chimera.LONGBOND_PBG_NAME, a1)
					for pb in pbs:
						pb.pseudoBondGroup.deletePseudoBond(pb)
					# get rid of bond
					m.deleteBond(b)

		# TODO: remove temporary directory?


_prologue = """
# loop modelling by the loopmodel class

import modeller.automodel as auto    # Load the automodel module

class my_model(auto.loopmodel):
	my_segments = ()

	def select_loop_atoms(self):
		v = info.version_info
		if isinstance(v, tuple) and v[0] < 9:
			# Modeller 8 code
			return self.select_loop_atoms_8()
		else:
			# Modeller 9 or SVN code
			return self.select_loop_atoms_9()

	def select_loop_atoms_8(self):
		status = 'initialize'
		for s in self.my_segments:
			self.pick_atoms(selection_segment=s,
				selection_search='segment', pick_atoms_set=1,
				res_types='all', atom_types='all',
				selection_from='all',
				selection_status=status)
			status = 'add'

	def select_loop_atoms_9(self):
		atmsel = selection()
		for s in self.my_segments:
			atmsel.add(self.residue_range(*s))
		return atmsel

log.verbose()	# request verbose output
env = environ()	# create a new MODELLER environment to build this model in

# directories for input atom files
env.io.atom_files_directory = '.'
# read all of the atoms in from original file
env.io.hetatm = True
env.io.water = True

segments = (
"""

_epilogue = """
)

a = my_model(env,
	inimodel = '%s',		# initial model of the target
	sequence = '%s')		# code of the target
a.my_segments = segments		# restrict modelling to segments
a.loop.starting_model = 1		# index of the first model
a.loop.ending_model = %d		# index of the last model
a.loop.md_level = %s	# loop refinement method
a.make()
"""

def writeModeller(f, name, seqname, loops, count, refine):
	"""output Modeller loop optimization file"""
	f.write(_prologue)
	prefix = ""
	for start, end in loops:
		print >> f, "\t('%s', '%s')," % (start, end)
	if refine == 'none':
		refine = 'None'
	else:
		refine = 'auto.refine.' + refine.replace(' ', '_')
	f.write(_epilogue % (name, seqname, count, refine))

import re
import os
pat = re.compile(r'.*\.(BL\d{8}\.pdb|DL\d{8})$')
def loopFileCount(dir=dir, max=max):
	count = 0
	for fn in os.listdir(dir):
		if pat.match(fn):
			count += 1
	return count / (2.0 * max)

def makedock(dirname, residueIds, outsideAtoms):
	outfn = os.path.join(dirname, 'dock.ent')
	out = open(outfn, 'w')
	found_file = False
	outsideResidueIds = set([id for id, name in outsideAtoms])
	def isOutside(id, name):
		if id not in outsideResidueIds:
			return False
		name = name.strip()
		for oid, oname in outsideAtoms:
			if id == oid and name == oname:
				return True
		return False
	for fn in os.listdir(dirname):
		if not fn.endswith('.pdb') or not pat.match(fn):
			continue
		found_file = True
		number = int(fn[-12:-8])
		print >> out, "REMARK     Number:", number
		conect = set()
		f = open(os.path.join(dirname, fn), 'rU')
		for line in f:
			if line.startswith('CONECT'):
				serial = int(line[6:11])
				if serial in conect:
					out.write(line)
				continue
			if not line.startswith('ATOM') \
			and not line.startswith('HETATM'):
				out.write(line)
				continue
			chain = line[21]
			pos = int(line[22:26])
			insertCode = line[26]
			id = chimera.MolResId(chain, pos, insert=insertCode)
			if id in residueIds or isOutside(id, line[12:16]):
				serial = int(line[6:11])
				conect.add(serial)
				out.write(line)
		f.close()
	out.close()
	if found_file:
		return outfn
	os.remove(outfn)
	return None
