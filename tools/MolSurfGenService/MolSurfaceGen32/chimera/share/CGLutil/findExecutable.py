Suffixes = [ ".exe" ]
import os

def findExecutable(name, alwaysAddSuffix=False):
	"""Find an executable file matching given name.
	
	The CHIMERA bin directory is checked first, then
	directories listed in the PATH environment variable,
	followed by a list of "standard" directories."""

	execNames = _getExecNames(name, alwaysAddSuffix)
	if os.path.isabs(name):
		for e in execNames:
			if os.access(e, os.X_OK):
				return e
		return None
	path = os.getenv("PATH", os.defpath)
	pathList = path.split(os.pathsep)
	chimera = os.getenv('CHIMERA')
	if chimera:
		pathList.insert(0, os.path.join(chimera, 'bin'))
	del chimera
	for p in pathList:
		for e in execNames:
			filename = os.path.join(p, e)
			if os.access(filename, os.X_OK):
				return filename
	return _findInstalledApp(execNames)

def _getExecNames(name, alwaysAddSuffix):
	if not alwaysAddSuffix:
		root, suffix = os.path.splitext(name)
		if not suffix:
			alwaysAddSuffix = True
	if alwaysAddSuffix:
		execNames = [ name + suffix for suffix in Suffixes ]
		execNames.insert(0, name)
	else:
		execNames = [ name ]
	return execNames

import sys
InstallDirs = [ ]
if sys.platform == "win32":
	import _winreg
	h = None
	try:
		h = _winreg.OpenKeyEx(_winreg.HKEY_LOCAL_MACHINE,
			"SOFTWARE\\Microsoft\\Windows\\CurrentVersion", 0,
			_winreg.KEY_QUERY_VALUE)
		pf = _winreg.QueryValueEx(h, "ProgramFilesDir")[0].encode('mbcs')
	except WindowsError:
		pf = os.path.join(os.path.splitdrive(sys.executable)[0],
						os.sep, "Program Files")
	_winreg.CloseKey(h)
	del h, _winreg
	try:
		dirList = os.listdir(pf)
	except OSError:
		pass
	else:
		for dname in dirList:
			dir = os.path.join(pf, dname)
			if os.path.isdir(dir):
				InstallDirs.append(dir)
		if dirList:
			del dname, dir
		del dirList
	del pf
else:
	InstallDirs.extend([
		"/usr/local/bin",
		"/usr/bin"
		"/bin",
	])

def _findInstalledApp(execNames):
	for dir in InstallDirs:
		for e in execNames:
			filename = os.path.join(dir, e)
			if os.access(filename, os.X_OK):
				return filename
	return None
