# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import regpass

regpass.setup()

def runServer(daemon=1, password=None):
	import server
	s = server.RegistrationServer('SACS-00', daemon=daemon,
					password=password)
	s.run()

def register(data):
	import client
	c = client.RegistrationClient()
	return c.register(data)
