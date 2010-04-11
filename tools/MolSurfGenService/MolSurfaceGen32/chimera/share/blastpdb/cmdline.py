# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def run(cmdName, args):
	from Midas.midas_text import doExtensionFunc
	if cmdName[0] == "b":
		f = blast
	elif cmdName[0] == "p":
		f = psiblast
	else:
		from chimera import UserError
		raise UserError("unknown command: \"%s\"" % cmdName)
	doExtensionFunc(f, args, specInfo=[("spec", "molecules", "molecules")])

def blast(molecules, db="pdb", evalue="1e-3", matrix="BLOSUM62", passes="3"):
	if len(molecules) != 1:
		from chimera import UserError
		raise UserError("exactly one molecule may be specified")
	import gui
	gui.blastprotein(molecules[0], "blast", db, evalue, matrix, passes)

def psiblast(molecules, db="pdb", evalue="1e-3", matrix="BLOSUM62", passes="3"):
	if len(molecules) != 1:
		from chimera import UserError
		raise UserError("exactly one molecule may be specified")
	import gui
	gui.blastprotein(molecules[0], "psiblast", db, evalue, matrix, passes)
