# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def minimize(molecules=None, nsteps=100, stepsize=0.02,
		interval=10, nogui=False, freeze=None, addhyd=True):
	import base
	import chimera
	if molecules is None:
		molecules = chimera.openModels.list(
				modelTypes=[chimera.Molecule])

	if freeze is None:
		freeze = base.FreezeNone
	elif base.FreezeNone.startswith(freeze):
		freeze = base.FreezeNone
	elif base.FreezeSelected.startswith(freeze):
		freeze = base.FreezeSelected
	elif base.FreezeUnselected.startswith(freeze):
		freeze = base.FreezeUnselected
	else:
		from chimera import UserError
		raise UserError("unknown freeze mode: \"%s\"" % freeze)
	def run(minimizer):
		minimizer.run()
	minimizer = base.Minimizer(molecules, nsteps=nsteps, stepsize=stepsize,
					interval=interval,
					freeze=freeze, nogui=nogui,
					addhyd=addhyd, callback=run)

def dynamics(molecules=None, nsteps=100, interval=10):
	import chimera
	raise chimera.LimitationError("MD not implemented yet")
