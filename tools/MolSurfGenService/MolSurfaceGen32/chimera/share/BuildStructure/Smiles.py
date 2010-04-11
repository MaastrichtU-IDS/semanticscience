# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Smiles.py 27965 2009-06-30 19:43:32Z pett $

import chimera

def openSmiles(smiles, resName="UNK"):
	m = smiles2mol(smiles, resName=resName)
	chimera.openModels.add([m])
	return m

def smiles2mol(smiles, resName="UNK"):
	if len(smiles) <= 14:
		identifyAs = "smiles:" + smiles
	else:
		identifyAs = "smiles:" + smiles[:14] + "..."
	from chimera.fetch import fetch_file
	path, headers = fetch_file("http://cheminfo.informatics.indiana.edu/rest/thread/d3.py/SMILES/%s" % smiles, identifyAs)
	from ReadSDF import readSDF
	m = readSDF(path, identifyAs=identifyAs)[0]
	m.residues[0].type = resName
	return m



