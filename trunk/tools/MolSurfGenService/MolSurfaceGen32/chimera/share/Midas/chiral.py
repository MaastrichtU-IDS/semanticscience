# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: chiral.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.bondGeom import bondPositions
multBond = ['Car', 'Oar', 'Npl']
carOar = ['C', 'O']
bonds = []
def init(atom):
	layer1 = atom.primaryNeighbors()
	global bonds
	bonds = [a.xformCoord() for a in layer1]
	try:
		var = chimera.idatm.typeInfo[atom.idatmType].substituents
	except KeyError:
		var = 4	
	layer1 = fakeHydrogenAdd(layer1, var, atom)
	global chiralAtom
	chiralAtom = atom
	try:
		layer1.sort(comp)
	except ChiralityError:
		return None	
	xf = chimera.Xform.lookAt(atom.xformCoord(),
			layer1[0].xformCoord(), layer1[3].xformCoord())
	nextpt = xf.apply(layer1[2].xformCoord())
	if nextpt.x > 0:
		return 'R'
	else:
		return 'S'
def comp(a, b):
	val = prioritySort([a], [b],
		{chiralAtom: True, a: True}, {chiralAtom: True, b: True})
	if val == 0:
		raise ChiralityError, "No chirality"
	return val
										
def scmp(a1, a2):
	val = cmp(a1.element.number, a2.element.number)
	if val != 0:
		return val
	return cmp(a1.element.mass, a2.element.mass)

def prioritySort(list1, list2, visited1, visited2):
	list1.sort(scmp)
	list2.sort(scmp)
	list1.reverse()
	list2.reverse()
	for i in range(min(len(list1), len(list2))):
		val = scmp(list1[i], list2[i])
		if val == 0:
			continue
		else:
			return val
	if len(list1) == len(list2):
		nlist1 = nextLevel(list1, visited1)
		nlist2 = nextLevel(list2, visited2)
		if nlist1:
			if nlist2:
				return prioritySort(nlist1, nlist2,
							visited1, visited2)
			return 1
		elif nlist2:
			return -1
		else:
			return 0
	elif len(list1) > len(list2):
		return 1
	else:
		return -1

def nextLevel(thisLevel, visited):
	for i in thisLevel:
		visited[i] = True
	nxtlvl = []
	for i, thisMember in enumerate(thisLevel):
		temp = thisMember.primaryNeighbors()
		try:
			typeInfo = chimera.idatm.typeInfo[thisMember.idatmType]
		except KeyError:
			continue
		tempvar = typeInfo.substituents
		if len(temp) < tempvar:
			temp = fakeHydrogenAdd(temp, tempvar, thisMember)
		if typeInfo.geometry == 3 or typeInfo.geometry == 2:
			temp = multBondsAdd(temp, typeInfo)
		if typeInfo in multBond:
			temp = fakeHalfAtomAdd(temp, thisMember)
		nxtlvl += filter(lambda x: x not in visited, temp)
	return nxtlvl

def fakeHydrogenAdd(primeBond, substit, curr):
	val = substit - len(primeBond)
	x = 0
	fh = FakeHydrogen(curr)
	while x < val:
		primeBond.append(fh)
		x = x+1
	return primeBond

def multBondsAdd(primeBond, curr):
	for i in range(len(primeBond)):
		try:
			lookup = chimera.idatm.typeInfo[primeBond[i].idatmType]
		except KeyError:
			continue	
		if lookup.geometry == curr.geometry:
			if lookup not in multBond and curr not in multBond:
				if curr.geometry == 2:
					primeBond.append(primeBond[i])
					primeBond.append(primeBond[i])
				else:
					primeBond.append(primeBond[i])
	return primeBond

def fakeHalfAtomAdd(primeBond, curr):
	aromatic = []
	if isAromatic(curr):
		for i in range(len(primeBond)):
			if isAromatic(primeBond[i]):
				aromatic.append(primeBond[i])
	counter = 1
	for i in range(len(aromatic)):
		if counter == 2:
			primeBond.append(FakeHalfAtom(aromatic[i-1],
								aromatic[i]))
			counter = 1
		else:
			counter = counter +1
	return primeBond

def isAromatic(atom):
	aName = atom.element.name
	if aName in carOar:
		lookup = chimera.idatm.typeInfo[atom.idatmType]
		if lookup in multBond:
			return True
		return False
	lookup = chimera.idatm.typeInfo[atom.idatmType]
	if lookup.geometry == 3:
		rings = atom.minimumRings(False)
		if rings:
			return True
		return False
	return False

class ChiralityError(Exception):
	pass

class FakeHydrogen:
	def __init__(self, atm):
		self.bonded = atm
	element = chimera.Element(1)
	def primaryNeighbors(self):
		return [self.bonded]
	def oslIdent(self):
		return 'FakeHydrogen'
	idatmType = 'HC'
	def xformCoord(self):
		primary = self.primaryNeighbors()[0]
		pos = bondPositions(primary.xformCoord(), 4, 1.0, bonds)
		class FakeCoord:
			pass	
		crd = FakeCoord()
		crd = pos[0]
		return crd
 
class FakeElement:
	def __init__(self, atm1, atm2):
		self.number = (atm1.element.number + atm2.element.number) / 2
		self.mass = (atm1.element.mass + atm2.element.mass) / 2

class FakeHalfAtom:
	def __init__(self, atm1, atm2):
		self.element = FakeElement(atm1, atm2)
	idatmType = 'HC'
	def primaryNeighbors(self):
		return [self.bonded]
