import chimera
from chimera.idatm import typeInfo
from chimera.selection import Selection, ItemizedSelection


def writeLeaprc(tempDir, topfile,  parmset, leaprc ) :
	import os
	f = open( leaprc, 'w' )
	f.write( "source leaprc." + parmset + "\n" )
	f.write( "source leaprc.gaff\n" )
        f.write( "set default rearrangeResidue on\n" )
	f.write( "tmp = loadmol2 " + os.path.join(tempDir, "sleap.in.mol2\n") )
	f.write( "parmchk tmp\n" )
	if topfile.endswith(".prmtop"):
		crdfile = topfile[:-7] + ".inpcrd"
	else:
		crdfile = topfile + ".inpcrd"
	f.write( "saveamberparm tmp " + topfile + " " + crdfile + "\n" )
	f.write( "quit\n" )



def writePrmtop(m, topfile, parmset, unchargedAtoms=None):
	import os
	import chimera
	from chimera import replyobj
	from WriteMol2 import writeMol2
	from tempfile import mkdtemp

	status = replyobj.status

	if unchargedAtoms and parmset.lower().endswith("ua"):
		# united atom
		replyobj.warning("Some uncharged/untyped protons expected due"
			" to use of united-atom force field.\n")
		unchargedHeavy = []
		skip = []
		for uncharged in unchargedAtoms.values():
			for uc in uncharged:
				if uc.element.number == 1:
					skip.append(uc)
				else:
					unchargedHeavy.append(uc)
		unchargedAtoms = unchargedHeavy
	else:
		skip = []
	if unchargedAtoms:
		if chimera.nogui:
			raise ValueError("Some atoms don't have charges/types")
		from chimera.baseDialog import AskYesNoDialog
		d = AskYesNoDialog("Some atoms don't have charges/types"
			" assigned.  Write prmtop anyway?")
		if d.run(chimera.tkgui.app) == "no":
			return
	tempDir = mkdtemp()

	def _clean():
		for fn in os.listdir(tempDir):
			os.unlink(os.path.join(tempDir, fn))
		os.rmdir(tempDir)

	sleapIn = os.path.join(tempDir, "sleap.in.mol2")
	writeMol2([m], sleapIn, status=status, gaffType=True, skip=skip)

	leaprc = os.path.join(tempDir, "solvate.cmd")
	writeLeaprc(tempDir, topfile, parmset, leaprc)

	chimeraRoot = os.environ["CHIMERA"]
        amberHome = os.path.join(chimeraRoot, "bin", "amber10")
        acHome = os.path.join(chimeraRoot, "bin", "antechamber")


	command = [os.path.join(amberHome, "exe", "sleap"), "-f", leaprc]

	
	print 'command: ', command
	if status:
		status("Running sleap" )
	from subprocess import Popen, STDOUT, PIPE
	# For some reason on Windows, if shell==False then antechamber
	# cannot run bondtype via system().
	import sys
	if sys.platform == "win32":
		shell = True
	else:
		shell = False
	replyobj.info("Running sleap command: %s\n" % " ".join(command))
	import os
	os.environ["AMBERHOME"]=amberHome
        os.environ["ACHOME"]=acHome
	sleapMessages = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
			cwd=tempDir, shell=shell, bufsize=1).stdout
	while True:
		line = sleapMessages.readline()
		if not line:
			break
		replyobj.status("(writeprmtop) %s" % line, log=True)
	if not os.path.exists(topfile):
		_clean()
		from chimera import NonChimeraError
		raise NonChimeraError("Failure running sleap \n"
			"Check reply log for details\n")
	else:
		replyobj.status("Wrote parmtop file %s\n" % topfile, log=True)

