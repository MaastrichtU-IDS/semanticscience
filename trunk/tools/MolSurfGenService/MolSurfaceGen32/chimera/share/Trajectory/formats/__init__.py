# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

import os

formats = []
head, tail = os.path.split(__file__)
for f in os.listdir(head):
	if os.path.exists(os.path.join(head, f, '__init__.py')):
		try:
			exec "from %s import formatName" % f
		except ImportError:
			formats.append(f)
		else:
			formats.append(formatName)
formats.sort(lambda a, b: cmp(a.lower(), b.lower()))

del f, head, tail, os
