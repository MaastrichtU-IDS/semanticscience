# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

import os, os.path

infos = []
for f in os.listdir(os.path.split(__file__)[0]):
	if not f[0].isalpha() or not f.endswith(".py") or f.startswith("mk"):
		continue
	try:
		exec("from %s import fragInfo" % f[:-3])
	except ImportError:
		from chimera import replyobj
		replyobj.error("Cannot get fragment info for %s" % f[:-3])
	infos.append(fragInfo)
