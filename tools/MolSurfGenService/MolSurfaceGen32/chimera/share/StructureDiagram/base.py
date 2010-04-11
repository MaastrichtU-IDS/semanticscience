# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

AtomLimit = 100

def smiles2image_Guha(smiles, width, height, scale):
	"Convert SMILES into JPEG using web service"
	from SurfaceAreaVolume import multipart
	fields = (
		( "smiles",	None,	str(smiles)	),
		( "width",	None,	str(width)	),
		( "height",	None,	str(height)	),
		( "scale",	None,	str(scale)	),
	)
	v = multipart.post_multipart_formdata(
			"cheminfo.informatics.indiana.edu",
			"/~rguha/code/java/cdkws/phpsdg.php", fields)
	retcode, msg, headers, data = v
	if retcode != 200:
		raise IOError(msg)
	from StringIO import StringIO
	from PIL import Image
	return Image.open(StringIO(data))

# ---------------------------------------------------------------

CactusFields = [
	( "disk",	None,	"off"		),
	( "hadd",	None,	"add"		),
	( "format",	None,	"PNG"		),
	( "interlace",	None,	"0"		),
	( "atomcolor",	None,	"type"		),
	( "asymbol",	None,	"symbol"	),
	( "hcolor",	None,	""		),
	( "csymbol",	None,	"special"	),
	( "hsymbol",	None,	"special"	),
	( "bondcolor",	None,	"split"		),
	( "bgcolor",	None,	"transparent"	),
	( "border",	None,	"10"		),
	( "wedges",	None,	"1"		),
	( "dashes",	None,	"1"		),
	( "docrop",	None,	"off"		),
	( "crop",	None,	"2"		),
	( "align",	None,	"none"		),
	( "coord",	None,	"0"		),
	( "new2d",	None,	"on"		),
	( "imagemap",	None,	"none"		),
	( "headercolor",None,	"Black"		),
	( "header",	None,	""		),
	( "footercolor",None,	"Black"		),
	( "footer",	None,	""		),
	( "commenttype",None,	"none"		),
	( "comment",	None,	""		),
	( "structure",	None,	"smiles"	),
]
CactusHost = "cactus.nci.nih.gov"
CactusScript = "/scripts/gifcreator.tcl"
#CactusHost = "www.cgl.ucsf.edu"		# for testing
#CactusScript = "/cgi-bin/test-cgi"

def smiles2image_Cactus(smiles, width, height, scale=1.0, **kw):
	fields = [
		( "smiles",	None,	str(smiles) ),
		( "file",	"",	""),
	]
	return _callCactus(fields, width, height, scale, **kw)

def molecule2image_Cactus(m, width, height, scale=1.0, **kw):
	from OpenSave import osTemporaryFile
	from chimera import PDBio
	import os
	fields = [ ( "smiles", None, "" ) ]
	tempFile = osTemporaryFile(suffix=".pdb", prefix="m2i_")
	try:
		pdbio = PDBio()
		pdbio.writePDBfile([m], tempFile)
		f = open(tempFile, "r")
		fields.append(("file", m.name + ".pdb", f.read()))
		f.close()
	finally:
		os.remove(tempFile)
	return _callCactus(fields, width, height, scale, **kw)

def _callCactus(fields, width, height, scale, **kw):
	from SurfaceAreaVolume import multipart
	fields.append(("width", None, str(width)))
	fields.append(("height", None, str(height)))
	fields.append(("bonds", None, str(1.0 / scale)))
	for fieldName, source, value in CactusFields:
		fields.append((fieldName, source, kw.get(fieldName, value)))
	v = multipart.post_multipart_formdata(CactusHost, CactusScript, fields)
	retcode, msg, headers, data = v
	if retcode != 200:
		raise IOError(msg)
	import re
	m = re.match(""".*<img src="(?P<path>[^"]+)".*""", data,
			re.M | re.S | re.I)
	if not m:
		raise IOError("Unexpected output:\n%s" % data)
	path = m.group("path")
	import urllib2
	f = urllib2.urlopen("http://%s%s" % (CactusHost, path))
	data = f.read()
	f.close()
	from StringIO import StringIO
	from PIL import Image
	return Image.open(StringIO(data))

# ---------------------------------------------------------------

Smi2gifFields = [
	( "atomcolor",		None,	"type"		),
	( "asymbol",		None,	"symbol"	),
	( "bondcolor",		None,	"split"		),
	( "border",		None,	"10"		),
	( "commenttype",	None,	"none"		),
	( "csymbol",		None,	"special"	),
	( "dashes",		None,	"1"		),
	( "format",		None,	"png"		),
	( "hcolor",		None,	""		),
	( "hsymbol",		None,	"special"	),
	( "interlace",		None,	"0"		),
	( "structure",		None,	"smiles"	),
	( "wedges",		None,	"1"		),
	( "antialiasing",	None,	"3"		),
	( "bgcolor",		None,	"transparent"	),
]
Smi2gifHost = "chimeraservices.compbio.ucsf.edu"
Smi2gifScript = "/cgi-bin/smi2gif.cgi"
#Smi2gifHost = "www.cgl.ucsf.edu"		# for testing
#Smi2gifScript = "/cgi-bin/test-cgi"

def smiles2image_Smi2gif(smiles, width, height, scale=1.0, **kw):
	fields = [
		( "smiles",	None,	str(smiles) ),
	]
	return _callSmi2gif(fields, width, height, scale, **kw)

def molecule2image_Smi2gif(m, width, height, scale=1.0, **kw):
	from OpenSave import osTemporaryFile
	from chimera import PDBio
	import os
	tempFile = osTemporaryFile(suffix=".pdb", prefix="m2i_")
	try:
		pdbio = PDBio()
		pdbio.writePDBfile([m], tempFile)
		f = open(tempFile, "r")
		fields = [ ( "inlinefile", m.name + ".pdb", f.read() ) ]
		f.close()
	finally:
		os.remove(tempFile)
	return _callSmi2gif(fields, width, height, scale, **kw)

def _callSmi2gif(fields, width, height, scale, **kw):
	from SurfaceAreaVolume import multipart
	fields.append(("width", None, str(width)))
	fields.append(("height", None, str(height)))
	fields.append(("bonds", None, str(1.0 / scale)))
	for fieldName, source, value in Smi2gifFields:
		fields.append((fieldName, source, kw.get(fieldName, value)))
	v = multipart.post_multipart_formdata(Smi2gifHost, Smi2gifScript, fields)
	retcode, msg, headers, data = v
	if retcode != 200:
		raise IOError(msg)
	from StringIO import StringIO
	from PIL import Image
	return Image.open(StringIO(data))

# ---------------------------------------------------------------

#smiles2image = smiles2image_Cactus
smiles2image = smiles2image_Smi2gif
#molecule2image = molecule2image_Cactus
molecule2image = molecule2image_Smi2gif

if __name__ == "chimeraOpenSandbox":
	img = smiles2image("c1ccncc1", 48, 48)
	img.save("test.png")
