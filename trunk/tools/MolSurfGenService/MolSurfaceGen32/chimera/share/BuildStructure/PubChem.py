# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: PubChem.py 29337 2009-11-18 00:03:53Z pett $

import chimera

def openPubChem(pcID, resName="UNK"):
	m = pubChem2mol(pcID, resName=resName)
	chimera.openModels.add([m])
	return m

def pubChem2mol(pcID, resName="UNK"):
	from chimera import fetch
	path, headers = fetch.fetch_file(
	"http://cheminfo.informatics.indiana.edu/rest/db/pub3d/%s" % pcID, pcID)
	from ReadSDF import readSDF
	m = readSDF(path, identifyAs="CID %s" % pcID)[0]
	m.residues[0].type = resName
	return m
