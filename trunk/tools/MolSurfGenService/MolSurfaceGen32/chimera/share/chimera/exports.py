"""keep track of export file formats for 3D scenes"""

# add new built-in formats at end of this file

def register(name, glob, suffix, command, notes=None):
	"""register new export file type"""
	_exportInfo[name] = {
		'glob': glob,
		'suffix': suffix,
		'command': command,
		'notes': notes
	}

def getFilterInfo():
	"""get list of export file types in the right format for a Save dialog"""
	fileTypes = _exportInfo.keys()
	fileTypes.sort()
	filterInfo = [
		(i, _exportInfo[i]['glob'], _exportInfo[i]['suffix'])
		for i in fileTypes
	]
	return filterInfo

def getNotes(name):
	"""Get the (html) notes for a particular export file type"""
	notes = _exportInfo[name]['notes']
	if not notes:
		notes = "<i>No additional information available.</i>"
	return notes

def doExportCommand(name, filename):
	"""Export the scene to filename with the given export file type"""
	import chimera
	if chimera.nogui and chimera.opengl_platform() != 'OSMESA':
		raise chimera.UserError, "Need graphics to export data (or use headless Linux version)"
	import replyobj
	replyobj.status("Exporting %s data to %s" % (name, filename))
	_exportInfo[name]['command'](filename)
	replyobj.status("Finished exporting %s." % filename)

# default "built-in" export information support

def _x3d(filename):
	import chimera
	title=""
	try:
		chimera.viewer.x3dWrite(filename, title)
	except IOError, v:
		raise chimera.NonChimeraError("Error writing x3d file: " + str(v))
	except chimera.error, v:
		raise chimera.UserError(v)

def _x3dConvert(prog, filename):
	import chimera, os
	title=""
	prog = os.path.join(os.environ["CHIMERA"], "bin", prog)
	try:
		from SubprocessMonitor import Popen, PIPE
		cmd = [prog, '-o', filename]
		proc = Popen(cmd, stdin=PIPE)
		chimera.viewer.x3dWrite(proc.stdin, 0, title)
		proc.stdin.close()
		returncode = proc.wait()
		if returncode == 1:
			raise chimera.NonChimeraError("Error writing %s"
							% (filename))
		elif returncode != 0:
			raise RuntimeError("'%s' exited with error code %d"
							% (prog, returncode))
	except chimera.error, v:
		raise chimera.UserError(v)

def _exportSTL(filename):
	# Determine endian-ness
	import struct
	if struct.pack("h", 1) == "\000\001":
		big_endian = 1
	else:
		big_endian = 0
	if big_endian:
		raise chimera.NonChimeraError("Only support STL output on little-endian computers")
	return _x3dConvert("x3d2stl", filename)

_exportInfo = {
	'VRML': {
		'glob': ('*.wrl', '*.vrml'),
		'suffix': ".wrl",
		'command': lambda filename: _x3dConvert("x3d2vrml", filename),
		'notes': "Exports scene in"
			" <a href='http://www.web3d.org/x3d/vrml/'>VRML97</a>"
			" (<i>a.k.a.</i>, VRML 2.0) format."
			"  Not supported: hither/yon clipping, per-model"
			" clipping planes, depth-cueing, stereo,"
			" dashed lines."
	},
	"POV-Ray": {
		'glob': "*.pov",
		'suffix': ".pov",
		'command': lambda filename: _x3dConvert("x3d2pov", filename),
		'notes': "Export scene in the"
			" <a href='http://www.povray.org'>POV-Ray</a>"
			" scene description language." 
			"  Not supported: hither/yon clipping,"
			" depth-cueing, stereo, dashed lines."
	},
	"RenderMan": {
		'glob': "*.rib",
		'suffix': ".rib",
		'command': lambda filename: _x3dConvert("x3d2RM", filename),
		'notes': "Export scene in"
			" <a href='http://www.renderman.org'>RenderMan</a>"
			" Interface Bytestream."
			"  Not supported: stereo, dashed lines."
	},
	"X3D": {
		'glob': "*.x3d",
		'suffix': ".x3d",
		'command': _x3d,
		'notes': "Export scene in the"
			" <a href='http://www.web3d.org/x3d/'>X3D</a>"
			" XML-enabled 3D file format."
			"  Not supported: hither/yon clipping, per-model"
			" clipping planes, depth-cueing."
			"  Although there are annotations for everything but"
			" stereo."
	},
	"STL": {
		'glob': "*.stl",
		'suffix': ".stl",
		'command': _exportSTL,
		'notes': "Export scene in the binary"
		" <a href='http://en.wikipedia.org/wiki/STL_(file_format)'>"
			"STL</a> triangle file format."
			"  Not supported: hither/yon clipping, per-model"
			" clipping planes, color, points, lines, text,"
			" and stereo."
	}
}
