from Rotamers import NoResidueRotamersError, RotamerParams

baseDescription = "Richardson lab backbone-independent rotamer library"
citeName = "Richardson"
citation = """SC Lovell, JM Word, JS Richardson and DC Richardson (2000)
The penultimate rotamer library
Proteins: Structure Function and Genetics 40: 389-408."""
cisTrans = ["PRO"]

def getParams(resName, fileName, cache, archive):
	try:
		return cache[fileName]
	except KeyError:
		pass
	import os.path
	myDir = os.path.split(__file__)[0]
	from zipfile import ZipFile
	zf = ZipFile(os.path.join(myDir, archive), "r")
	try:
		data = zf.read(fileName)
	except KeyError:
		raise NoResidueRotamersError("No rotamers for %s" % resName)
	from struct import unpack, calcsize
	sz1 = calcsize("!ii")
	numRotamers, numParams = unpack("!ii", data[:sz1])
	sz2 = calcsize("!f%di" % (numParams-1))
	rotamers = []
	for i in range(numRotamers):
		params = unpack("!f%di" % (numParams-1),
						data[sz1+i*sz2:sz1+(i+1)*sz2])
		p = params[0]
		chis = params[1:]
		rotamers.append(RotamerParams(p, chis))
	cache[fileName] = rotamers
	return rotamers
