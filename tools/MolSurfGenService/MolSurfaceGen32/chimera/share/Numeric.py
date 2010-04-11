"""This is a dummy Python module that raises a Chimera
LimitationError when modules try to use Numeric
instead of numpy."""

from chimera import LimitationError
class ImportLimitationError(LimitationError, ImportError):
	pass

raise ImportLimitationError(
		"This version of Chimera uses numpy for calculations.\n"
		"Numeric is only available in Chimera 1.2318 and earlier.")
