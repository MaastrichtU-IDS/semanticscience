# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: setup.py 26655 2009-01-07 22:02:30Z gregc $

# register a type with OpenModels for session PDB file
# do it here instead __init__ since __init__ is imported indirectly by chimera
import chimera
def _openSessionPDB(fileName, identifyAs=None):
	return chimera._openPDBModel(fileName, explodeNMR=False,
					fromSession=True, identifyAs=identifyAs)
							
chimera.fileInfo.register("session PDB", _openSessionPDB, None, [])
