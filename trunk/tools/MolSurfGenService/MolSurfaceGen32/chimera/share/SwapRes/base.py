# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: base.py 26655 2009-01-07 22:02:30Z gregc $

# new plan:  have 'getBackbone' (if that's what I want to keep calling it)
#   return two things:  a list of all the fixed heavy atom names in the
#   residue, and the name of the atom that the 'side chain' buds from (e.g.
#   CA) and two preceding atoms.
#
#   (if not 'preserve'):
#   Go through the current residue deleting all 'non-fixed' heavy atoms, 
#   while noting if hydrogens are present.  If they are present, make a
#   second pass, deleting all hydrogens 'orphaned' by the first pass.
#
#   (if 'preserve'):
#   something along the lines of start from 'bud' atom and add to 'fixed'
#   those that have correct IDATM types.  Make them 'buds' also.  Possibly
#   change atom name to template name.
#
#   From bud, find each bond that doesn't exist yet.  If the bonded atom
#   doesn't exist, add it and add it to the list of buds.  Add the bond.

from math import pi, cos, sin
import chimera
from chimera import angle, dihedral, cross, Coord
from chimera.molEdit import addAtom, addDihedralAtom, addBond
from chimera.idatm import tetrahedral, planar, linear, single, typeInfo
from chimera.bondGeom import bondPositions

class BackboneError(ValueError):
	pass

def swap(res, newRes, preserve=0, bfactor=True):
	"""change 'res' into type 'newRes'"""

	if res == "HIS":
		res = "HIP"
	fixed, buds, start, end = getResInfo(res)
	
	tmplRes = chimera.restmplFindResidue(newRes, start, end)
	if not tmplRes:
		raise ValueError, "No connectivity template for residue '%s'"\
									% newRes
	# sanity check:  does the template have the bud atoms?
	for bud in buds:
		if not tmplRes.atomsMap.has_key(bud):
			raise ValueError, "New residue type (%s) " \
			  "not compatible with starting residue type (%s)" \
			  				% (newRes, res.type)
		
	# if bfactor not specified, find highest bfactor in molecule
	# and use that for swapped-in atoms
	if bfactor is False:
		bfactor = None
	if bfactor is True:
		for a in res.molecule.atoms:
			try:
				if bfactor is True or a.bfactor > bfactor:
					bfactor = a.bfactor
			except AttributeError:
				pass

	if preserve:
		raise ValueError, "'preserve' keyword not yet implemented"

	# prune non-backbone atoms
	for a in res.oslChildren():
		if a.name not in fixed:
			a.molecule.deleteAtom(a)

	# add new sidechain
	while len(buds) > 0:
		bud = buds.pop()
		tmplBud = tmplRes.atomsMap[bud]
		resBud = res.atomsMap[bud][0]

		try:
			info = typeInfo[tmplBud.idatmType]
			geom = info.geometry
			subs = info.substituents
		except KeyError:
			print tmplBud.idatmType
			raise AssertionError, "Can't determine atom type" \
				" information for atom %s of residue %s" % (
				bud, res.oslIdent())

		# use coord() rather than xformCoord():  we want to set
		# the new atom's coord(), to which the proper xform will
		# then be applied
		for a, b in tmplBud.bondsMap.items():
			if a.element.number == 1:
				# don't add hydrogens
				continue
			if res.atomsMap.has_key(a.name):
				resBonder = res.atomsMap[a.name][0]
				if not resBud.bondsMap.has_key(resBonder):
					addBond(a, resBonder)
				continue

			newAtom = None
			numBonded = len(resBud.bonds)
			if numBonded >= subs:
				raise AssertionError, \
					"Too many atoms bonded to %s of" \
					" residue %s" % (bud, res.oslIdent())
			if numBonded == 0:
				raise AssertionError, \
					"Atom %s of residue %s has no" \
					" neighbors after pruning?!?" % (
					bud, res.oslIdent())
			elif numBonded == 1:
				# only one connected atom -- have to use
				# dihedral
				real1 = resBud.neighbors[0]
				newAtom = formDihedral(resBud, real1,
								tmplRes, a, b)
			elif numBonded == 2:
				crd = resBud.coord()
				bonded = resBud.neighbors
				bcrds = map(lambda a: a.coord(), bonded)
				positions = bondPositions(crd, geom,
							b.length(), bcrds)
				if len(positions) > 1:
					# need to disambiguate choices;
					# check improper dihedral

					# but first, make sure the bonded
					# atoms are in this residue
					inres = filter(lambda a, r=res:
							a.residue == r, bonded)
					if len(inres) == 0:
						raise AssertionError, \
						"Can't disambiguate " \
						"tetrahedral position by " \
						"forming in-residue dihedral " \
						"for %s of residue %s" % (
						bud, res.oslIdent())
					if len(inres) == 1:
						newAtom = formDihedral(resBud,
							inres[0], tmplRes, a, b)
					else:
						# okay, check improper dihedral
						tmplBonded = map(lambda a,
							tra=tmplRes.atomsMap:
							tra[a.name], bonded)
						tmplPts = map(lambda a:
							a.coord(), [a, 
							tmplBud] + tmplBonded)
						tmplDihed = apply(dihedral,
								tmplPts, {})
						backPts = map(lambda a:
							a.coord(), [resBud]
							+ bonded)
						dh1 = apply(dihedral, tuple(
								positions[:1]
								+ backPts), {})
						dh2 = apply(dihedral, tuple(
								positions[1:]
								+ backPts), {})
						diff1 = abs(dh1 - tmplDihed)
						diff2 = abs(dh2 - tmplDihed)
						if diff1 > 180:
							diff1 = 360 - diff1
						if diff2 > 180:
							diff2 = 360 - diff2
						if diff1 < diff2:
							position = positions[0]
						else:
							position = positions[1]
				else:
					position = positions[0]
			else:
				crd = resBud.coord()
				bonded = resBud.neighbors
				bcrds = map(lambda a: a.coord(), bonded)
				positions = bondPositions(crd, geom,
							b.length(), bcrds)
				if len(positions) > 1:
					raise AssertionError, \
						"Too many positions returned" \
						" for atom %s of residue %s" % (
						bud, res.oslIdent())
				position = positions[0]

			if not newAtom:
				newAtom = addAtom(a.name, a.element,
								res, position)
			newAtom.drawMode = resBud.drawMode
			if bfactor is not None and bfactor is not True:
				newAtom.bfactor = bfactor

			# TODO: need to iterate over coordSets
			for bonded in a.bondsMap.keys():
				if not res.atomsMap.has_key(bonded.name):
					continue
				addBond(newAtom, res.atomsMap[bonded.name][0])
			buds.append(newAtom.name)

	res.label = res.label.replace(res.type, newRes)
	res.type = newRes

aminoInfo = (("N", "CA", "C", "O", "OXT"), ("CA", "C", ("O", "OXT")))
nucleicInfo = (("O1P", "OP1", "O2P", "OP2", "P", "O5'", "C5'", "C4'", "C3'",
	"O3'", "C2'", "O2'", "C1'", "O4'"), ("C1'", "O4'", "C4'"))
def getResInfo(res):
	"""return a list of the fixed atoms of the residue, a list of
	   the fixed atoms that non-fixed atoms attach to, and whether
	   this residue is the start and/or end of a chain"""
	
	errmsg =  "Cannot identify backbone of residue %s (%s)" % (
						res.oslIdent(), res.type)
	backbone = []
	if res.atomsMap.has_key("N"):
		# putative amino acid
		basicInfo = aminoInfo
		start = len(res.atomsMap["N"][0].bonds) != 2
		end = res.atomsMap.has_key("OXT")
	elif res.atomsMap.has_key("O3'"):
		# putative nucleic acid
		basicInfo = nucleicInfo
		start = not res.atomsMap.has_key("P")
		end = len(filter(lambda a: a.element.name == "P",
				res.atomsMap["O3'"][0].neighbors)) == 0
		if end and res.atomsMap.has_key("O2'"):
			end = len(filter(lambda a: a.element.name == "P",
				res.atomsMap["O2'"][0].neighbors)) == 0
	else:
		raise BackboneError(errmsg)
	fixed, bud = basicInfo

	# must have the bud atoms present, (and resolve O/OXT ambiguity)
	finalBud = []
	for atName in bud:
		if isinstance(atName, tuple):
			for ambig in atName:
				if res.atomsMap.has_key(ambig):
					finalBud.append(ambig)
					break
			else:
				raise BackboneError(errmsg)
			continue
		if res.atomsMap.has_key(atName):
			finalBud.append(atName)
		else:
			raise BackboneError(errmsg)
	
	return (list(fixed), finalBud, start, end)


def formDihedral(resBud, real1, tmplRes, a, b):
	res = resBud.residue
	inres = filter(lambda a, rb=resBud, r=res: a.residue == r and a != rb,
							real1.neighbors)
	if real1.residue != res or len(inres) < 1:
		raise AssertionError, "Can't form in-residue dihedral for" \
				" %s of residue %s" % (bud, res.oslIdent())
	real2 = inres[0]
	xyz0, xyz1, xyz2 = map(lambda a, tr=tmplRes:
			tr.atomsMap[a.name].coord(), (resBud, real1, real2))

	xyz = a.coord()
	blen = b.length()
	ang = angle(xyz, xyz0, xyz1)
	dihed = dihedral(xyz, xyz0, xyz1, xyz2)
	return addDihedralAtom(a.name, a.element, resBud,
						real1, real2, blen, ang, dihed)
