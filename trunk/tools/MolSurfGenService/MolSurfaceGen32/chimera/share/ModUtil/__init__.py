# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

"""
ModUtil -- chimera utilities for Sali's Modeller
"""
import chimera

def resId(residue, strip=True):
	"""Take a chimera residue and return the modeller residue id"""

	id = residue.id
	result = '%s%s:%s' % (id.position, id.insertionCode, id.chainId)
	if strip:
		return result.replace(' ', '')
	return result

def toChimeraResId(resid):
	"""Take a Modeller residue id and convert it to a chimera one"""
	num, chain = resid.split(':')
	insertCode = ''
	while not str.isdigit(num[-1]):
		insertCode = num[-1] + insertCode
		num = num[:-1]
	pos = int(num)
	return chimera.MolResId(chain, pos, insert=insertCode)

def convertSelection(sel, minLen=4, molecule=None, keepHet=False, keepNA=False, turnsOnly=True):
	"""Take a chimera selection and convert it to a list of Modeller residue pairs
	

	"""
	selResidues = chimera.atomsBonds2Residues(sel.atoms(), sel.bonds())
	if molecule is None:
		# guess
		for r in selResidues:
			molecule = r.molecule
			break

	from chimera.resCode import nucleic3to1
	discard = set()
	for r in selResidues:
		if r.molecule != molecule \
		or (not keepHet and r.isHet) \
		or (not keepNA and r.type in nucleic3to1) \
		or (turnsOnly and (r.isHelix or r.isStrand)):
			discard.add(r)
	selResidues.difference_update(discard)
	if not selResidues:
		return [], set()

	loop = []
	result = []
	for r in molecule.residues:
		if r in selResidues:
			loop.append(r)
			continue
		if loop:
			if len(loop) >= minLen:
				result.append((resId(loop[0]), resId(loop[-1])))
			else:
				for i in loop:
					selResidues.discard(i)
			loop = []
	if loop:
		# one more at the end
		if len(loop) >= minLen:
			result.append((resId(loop[0]), resId(loop[-1])))
		else:
			for i in loop:
				selResidues.discard(i)
	return result, selResidues

def run(args, progressCallback=None, **keywords):
	"""Run executable (default is first argument) with given
	arguments in a subprocess.  Show a progress bar based on
	the number of files matching the given filepattern up to
	the maxcount."""

	kw = keywords.copy()
	import os
	import chimera.SubprocessMonitor as SM
	try:
		p = SM.Popen(args, daemon=True, progressCB=progressCallback, **kw)
	except OSError, e:
		raise
	if chimera.nogui and not progressCallback:
		return p
	if isinstance(args, basestring):
		text = args
	else:
		text = ' '.join(args)
	return SM.monitor("running '%s'" % text, p)
