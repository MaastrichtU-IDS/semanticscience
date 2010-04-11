#!/usr/bin/env python
"""chimera molecular modeling application """

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __main__.py 29540 2009-12-04 01:21:04Z gregc $

# Sometimes we freeze this __main__ module and place it in a custom Python
# interpreter for debugging or performance reasons:
#
#   Debugging because we can add debugging malloc's to the shared libraries.
#   Performance because the application-specific shared libraries can be
#   prelinked.

import sys, os

if os.environ.has_key('LD_PRELOAD'):
	# don't ever want to pass this down to the next program
	del os.environ['LD_PRELOAD']

if not os.environ.has_key('CHIMERA'):
	# Assume argv[0] is a absolute path to CHIMERA/share/__main__.py.
	path, file = os.path.split(sys.argv[0])
	if file == '__main__.py':
		path, file = os.path.split(path)
		if file == 'share':
			os.environ['CHIMERA'] = path
	if not os.environ.has_key('CHIMERA'):
		print >> sys.stderr, "Chimera is misconfigured.  Please reinstall chimera."
		raise SystemExit, 1

# Remove environment variables only used for Python startup
for env in ('PYTHONHOME', 'PYTHONPATH'):
	if os.environ.has_key(env):
		del os.environ[env]
del env

profile = "--profile" in sys.argv
if profile:
	sys.argv.remove("--profile")

# Add CHIMERA/share to path so 'import chimeraInit' should work.
sys.path.insert(0, os.path.join(os.environ['CHIMERA'], 'share'))

if "--debug" in sys.argv:
	# in debug mode, local directories override system ones
	sys.path.insert(0, os.getcwd())

try:
	import chimeraInit
except ImportError:
	print >> sys.stderr, "Chimera could not find an essential module: `chimeraInit.py'.  Please reinstall chimera."
	raise SystemExit, 1

if profile:
	import hotshot
	prof = hotshot.Profile("chimera.prof")
	value = prof.runcall(chimeraInit.init, sys.argv)
	prof.close()
	raise SystemExit, value
else:
	value = chimeraInit.init(sys.argv)
	raise SystemExit, value
