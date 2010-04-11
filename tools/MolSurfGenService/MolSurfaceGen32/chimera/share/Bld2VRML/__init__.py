import bld2vrml
import chimera
import OpenSave

def openBild(filename, identifyAs=None):
	f = OpenSave.osOpen(filename)
	try:
		return openFileObject(f, filename, identifyAs)
	finally:
		f.close()

def openBildString(s, identifyAs=None):
	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	f = StringIO.StringIO(s)
	return openFileObject(f, "<string>", identifyAs)

def openFileObject(f, filename, identifyAs=None):
	env = bld2vrml.Environment()
	lineno = 0
	try:
		for line in f:
			lineno += 1
			env.handleLine(line)
	except:
		import traceback
		traceback.print_exc()
		raise chimera.NotABug("%s: error at line %d"
					% (filename, lineno)) 
	env.finish()
	vrml = env.buildVRML()
	if identifyAs is None:
		identifyAs = filename
	return chimera._openVRMLModel(vrml, identifyAs=identifyAs)
