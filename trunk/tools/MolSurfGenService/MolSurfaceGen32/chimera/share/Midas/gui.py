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

import chimera.tkgui
import midas_ui
import os
import Midas

icon = os.path.join(Midas.__path__[0], 'midas.png')
chimera.tkgui.app.toolbar.add(icon, midas_ui.createUI, 'Show Midas Command Panel', None)
