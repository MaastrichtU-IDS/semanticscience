# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 26655 2009-01-07 22:02:30Z gregc $

import chimera

class Browser_Setup_EMO(chimera.extension.EMO):
    """Extension Management Object (EMO) for browser set-up interface"""

    def name(self):
	return "Browser Configuration"
    def description(self):
	return "Configure system to open supported file types with Chimera"
    def categories(self):
	return ['Utilities']
    def icon(self):
	return None
    def activate(self):
	import sys
	import chimera
	if sys.platform == 'darwin':
	    chimera.replyobj.warning(
		    "The 'Browser Configuration' tool does not yet work "
		    "on this platform. Please see the documentation for "
		    "details on how to manually configure your browser.")
	else:
	    self.module().ConfigBrowser()

## register with the Chimera extension manager
chimera.extension.manager.registerExtension(Browser_Setup_EMO(__file__))

#
# Initialize web access preferences
#
import DBPuppet.waprefs
