# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 27751 2009-06-04 00:33:23Z pett $

"""Save/restore most aspects of a Chimera modeling session"""

from save import saveSession, sessionID, noAutoRestore, autoRestorable, \
	sesRepr, SAVE_SESSION, BEGIN_RESTORE_SESSION, END_RESTORE_SESSION, \
	registerAttribute, colorID
RESTORE_SESSION = END_RESTORE_SESSION
