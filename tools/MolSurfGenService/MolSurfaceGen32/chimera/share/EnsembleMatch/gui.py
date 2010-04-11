# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import os.path
from chimera import tkgui
from choose import EnsembleMatchCB, EnsembleTileCB

dir = os.path.dirname(__file__)
icon = os.path.join(dir, 'ensembletile.tiff')
tkgui.app.toolbar.add(icon, EnsembleTileCB, 'Tile Ensemble Conformers', None)
icon = os.path.join(dir, 'ensemblematch.tiff')
tkgui.app.toolbar.add(icon, EnsembleMatchCB, 'Match Ensembles', None)
