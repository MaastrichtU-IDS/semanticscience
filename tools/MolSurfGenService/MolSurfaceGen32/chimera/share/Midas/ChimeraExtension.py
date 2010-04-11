# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

CMD_FILE_TYPE = "Chimera commands"
CMD_EXTENSIONS = [".com", ".cmd"]
CMD_PREFIXES = ["com", "cmd"]
def func(cmdFile):
	from Midas.midas_text import processCommandFile
	import os.path
	dirName, fileName = os.path.split(cmdFile)
	if dirName:
		if not os.path.exists(dirName):
			from Midas import MidasError
			raise MidasError(
				"No such folder/directory: %s" % dirName)
		import os
		cwd = os.getcwd()
		try:
			os.chdir(dirName)
			processCommandFile(fileName)
		finally:
			os.chdir(cwd)
	else:
		processCommandFile(cmdFile)
	return []
chimera.fileInfo.register(CMD_FILE_TYPE, func, CMD_EXTENSIONS, CMD_PREFIXES,
		category=chimera.FileInfo.SCRIPT)
del func, CMD_FILE_TYPE, CMD_EXTENSIONS, CMD_PREFIXES
