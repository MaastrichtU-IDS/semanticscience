# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26655 2009-01-07 22:02:30Z gregc $

import ResProp
from chimera import tkgui

import os
iconFile = os.path.join(ResProp.__path__[0], 'resprop.png')
tkgui.app.toolbar.add(iconFile, ResProp.doUI, 'Residue property coloring', None)
