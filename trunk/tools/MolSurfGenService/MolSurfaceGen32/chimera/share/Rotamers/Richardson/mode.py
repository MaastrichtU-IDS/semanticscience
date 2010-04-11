from shared import getParams, citation, baseDescription, citeName, cisTrans

displayName = "Richardson (mode)"
description = baseDescription

_independentCache = {}
def independentRotamerParams(resName):
	return getParams(resName, resName, _independentCache, "mode.zip")
