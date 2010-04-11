# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Amber.py 28439 2009-08-10 17:33:29Z pett $

import numpy
import os
import sys
import _amber
import chimera
from chimera import elements, replyobj

AmberToChimeraResMap = {
    "DAN":"DA",
    "DGN":"DG",
    "DCN":"DC",
    "DTN":"DT",
    "RAN":"A",
    "RGN":"G",
    "RCN":"C",
    "RUN":"T",
    "DC5":"DC",
    "DC3":"DC",
    "DC":"DC",
    "DA5":"DA",
    "DA3":"DA",
    "DA":"DA",
    "DG5":"DG",
    "DG3":"DG",
    "DG":"DG",
    "DT5":"DT",
    "DT3":"DT",
    "DT":"DT",
    "RC5":"C",
    "RC3":"C",
    "RC":"C",
    "RA5":"A",
    "RA3":"A",
    "RA":"A",
    "RG5":"G",
    "RG3":"G",
    "RG":"G",
    "RU5":"U",
    "RU3":"U",
    "RU":"U",
    }
AmberToChimeraResMapKeys = AmberToChimeraResMap.keys()

atom_type_to_elements = {
'CA': 'C',
'CB': 'C',
'CC': 'C',
'CK': 'C',
'CM': 'C',
'CN': 'C',
'CQ': 'C',
'CR': 'C',
'CT': 'C',
'CV': 'C',
'CW': 'C',
'C*': 'C',
'C0': 'C',
'F': 'F',
'H': 'H',
'HC': 'H',
'H1': 'H',
'H2': 'H',
'H3': 'H',
'HA': 'H',
'H4': 'H',
'H5': 'H',
'HO': 'H',
'HS': 'H',
'HW': 'H',
'HP': 'H',
'IM': 'Cl',
'IP': 'Na',
'NA': 'N',
'NB': 'N',
'NC': 'N',
'NT': 'N',
'N2': 'N',
'N3': 'N',
'N*': 'N',
'OW': 'O',
'OH': 'O',
'OS': 'O',
'O2': 'O',
'SH': 'S',
}

def MapResidue(residue):
    if residue not in AmberToChimeraResMapKeys:
        return residue
    return AmberToChimeraResMap[residue]

class Amber:
    # TrajName used by main interface when loading additional frames
    TrajName = "Trajectory/Restart"
    AddTrajKw = {
        'filters': [(TrajName, ["*.trj", "*mdcrd", "*.rst", "*.crd"])],
	'title': "Choose %s File" % TrajName,
	'historyID': "AmberTrajectory/Restart"
    }

    def __init__(self, prmtop, trajectory, startFrame, endFrame):
	self.elements = None
        self.prmtopFilename = prmtop
        self.name = os.path.basename(trajectory)
        self.trajectoryFilename = trajectory
	replyobj.status("Reading Amber prmtop\n", blankAfter=0)
	try:
		self.prmtop = Prmtop(prmtop)
	finally:
		replyobj.status("Done reading Amber prmtop\n")
	from Trajectory import MultiFileTrajectory
	self.trajectory = MultiFileTrajectory(
					lambda f: Trajectory(self.prmtop, f))
	self.trajectory.addFile(trajectory)
	self.startFrame = startFrame
	self.endFrame = endFrame

	replyobj.status("Creating bonds\n", blankAfter=0)
        self.bonds = []
        a1 = self.prmtop['BondAt1']
        a2 = self.prmtop['BondAt2']
        for i in range(len(a1)):
            b1 = a1[i] / 3
            b2 = a2[i] / 3
            self.bonds.append((b1, b2))
        a1 = self.prmtop['BondHAt1']
        a2 = self.prmtop['BondHAt2']
        for i in range(len(a1)):
            b1 = a1[i] / 3
            b2 = a2[i] / 3
            self.bonds.append((b1, b2))
	replyobj.status("Bonds created\n", blankAfter=0)

    def addTraj(self, trajFileName):
	replyobj.status("Reading %s file %s" % (self.TrajName, trajFileName),
								blankAfter=0)
	try:
		self.trajectory.addFile(trajFileName)
	finally:
		replyobj.status("Done reading %s file %s\n"
						% (self.TrajName, trajFileName))

## Wrapped access to prmtop data
    def GetDict(self, i):
        if i == "numatoms":
            return self.prmtop['Natom']
        if i == "atomnames":
            return self.prmtop['AtomNames']
        if i == "resnames":
            return [MapResidue(rn) for rn in self.prmtop['ResNames']]
        if i == "ipres":
	    return self.prmtop['Ipres']
	if i == "bonds":
	    return self.bonds
	if i == "elements":
	    if self.elements is None:
	    	self.computeElements()
	    return self.elements
	raise KeyError, "Can't GetDict() for '%s'" % i

    def SetDict(self, i, j):
        self.prmtop[i] = j

    def computeElements(self):
	self.elements = []
       	for i, atom_type in enumerate(self.prmtop['AtomSym']):
		try:
			elementName = atom_type_to_elements[atom_type.upper()]
		except KeyError:
			# use mass
			from Trajectory import determineElementFromMass
			el = determineElementFromMass(self.prmtop['Masses'][i])
		else:
			el = chimera.Element(elements.name.index(elementName))
		self.elements.append(el)

## Wrapped access to trajectory data
    def __getitem__(self, i):
        return self.trajectory[i-1]
    
    def __getslice__(self, i, j):
        return self.trajectory[i-1:j-1]

    def __len__(self):
	return len(self.trajectory)

    def __repr__(self):
        return "Amber interface:\n%s\n%s" % (self.prmtop.__repr__(), self.trajectory.__repr__())
                                                                 
class Prmtop:
    def __init__(self, prmtop):
        self.prmtopFilename = prmtop
	from OpenSave import osUncompressedPath
	self.prm = _amber.prmtop(osUncompressedPath(self.prmtopFilename))
	if self.prm == None:
	    raise IOError, "Could not open prm file %s" %  self.prmtopFilename
        self.prm['AtomNames'] = map(str.strip, self.prm['AtomNames'])
        self.prm['AtomSym'] = map(str.strip, self.prm['AtomSym'])
        self.prm['ResNames'] = map(str.strip, self.prm['ResNames'])

    def __getitem__(self, i):
	return self.prm[i]

    def __setitem__(self, i, val):
	self.prm[i] = val

    def __repr__(self):
        return "Amber prmtop: %s" % self.prmtopFilename

class Trajectory:
    def __init__(self, prmtop, trajectory, startFrame=None, endFrame=None, box=None, crlf=None, vel=0):
	self.prm = prmtop
	self.trajectoryFilename = trajectory
	from OpenSave import osUncompressedPath
	# since self.traj gets handed off to the C++ layer and
	# seek() is called on the underlying file descriptor,
	# can't use osOpen() which might return a gzipFile object
	self.realTrajectoryFile = osUncompressedPath(self.trajectoryFilename)
	self.crlf = crlf
	self.type = None
	self.length=0
	self.vel=vel


        ## future enhancement: user sets natoms (to read crd with different # of atoms)
	self.natom = self.prm['Natom']
	## if box == None, then get the box state from the prmtop file
	if box == None:
		if self.prm['IfBox'] >= 1:
			self.box = 1
		else:
			self.box = 0
	## otherwise, set the box state by the user's choice
	else:
		if box >= 1:
			self.box = 1
		if box == 0:
			self.box = 0

        ## Now, open the trajectory
	# since self.traj gets handed off to the C++ layer and
	# seek() is called on the underlying file descriptor,
	# can't use osOpen() which might return a gzipFile object
	self.traj = open(self.realTrajectoryFile, "rb")

	## read the header and figure out how long the trajectory is
	self.SetupFrame()
	if(self.type == 'bintraj'):
	    from Scientific.IO import NetCDF
	    self.traj = NetCDF.NetCDFFile(self.trajectoryFilename,'r')
	    self.coord = self.traj.variables['coordinates']
	    self.length = len(self.coord)
	else:
	    self.length = self.DetermineLength()


    def __repr__(self):
        return "Amber trajectory: %s (length: %d)" % (self.trajectoryFilename, self.length)

    def __getitem__(self, i):
	if i < 0 or i > int(self.length):
	    raise 'FrameError', 'Tried to read an invalid frame (%d of %d)' % (i, self.length)
	return self.ReadFrame(i)

    def __getslice__(self, i, j):
	if i < 0 or i > int(self.length):
	    raise 'FrameError', 'Tried to read an invalid frame (%d of %d)' % (i, self.length)

	if j < 0 or j > int(self.length):
	    raise 'FrameError', 'Tried to read an invalid frame (%d of %d)' % (j, self.length)

	frames = []

	for slice in range(i,j):
	    try:
		frame = self.ReadFrame(slice)
	    except:
		break
	    frames.append(frame)

	f= numpy.array(frames)
	del frames
	return f

    def __len__(self):
	if self.type in ['bintraj', 'traj']:
	    return int(self.length)
## a restart file is length 1 always
	else:
	    return 1

## calculate the seek offset to the beginning of a frame
## each frame has natom * 3 floats of length 8
## each line is 10 long, so every ten floats we add an extra for the linefeed
## if the frame isn't a multiple of ten long there is an extra linefeed(?)
## if there is a box, add an extra three floats plus linefeed
## for Windows, it's cr/lf instead of just lf

    def l(self):
	l = 1L * self.natom * 24 + (self.natom * 3 / 10)
	if self.crlf != None:
	    l = l + (self.natom * 3 / 10)
	if ((self.natom * 3) % 10) != 0:
	    l = l + 1
	    if self.crlf != None:
		l = l + 1
	if (self.box == 1):
	    l = l + 25
	    if self.crlf != None:
		l = l + 1
	return l

    def frameptr(self, frame):
	return self.initial + frame * self.l()


    ## this rather naive function determines the length of the trajectory
    ## by looking at the file size, (subtract off length of the header)
    def DetermineLength(self):
	stat = os.stat(self.realTrajectoryFile)
	filesize = stat[6]
	f = filesize-self.initial
	l = self.l()
	frames = f/l
	return frames

    def SetupFrame(self):
	current = self.traj.tell()
	self.traj.seek(0)
	title = self.traj.readline()
        title = title.strip()
	if title[:3] == 'CDF':
	    self.type = 'bintraj'
	else:
	    title = title.strip()
	    if len(title) > 80:
		raise IOError, "Trajectory/Restart header line is greater than 80 characters -- invalid!!"
	    self.initial = self.traj.tell()

	    firstline = self.traj.readline()
	    l = firstline.split()

	    if len(l) in (1,2):
		self.type = 'restart'
		self.initial = self.traj.tell()
	    else:
		self.type = 'traj'

	    self.traj.seek(current)


    def ReadFrame(self, frame):
	if self.type == 'bintraj':
	    newcrd = self.coord[frame]
	else:
	    crd = numpy.zeros((self.natom*3), numpy.float)
	    if self.type == 'traj':
		self.boxsize = _amber.ReadTrajectoryFrame( crd, self.natom, self.box, self.frameptr(frame), self.traj)
	    else:
		if frame != 0:
		    raise 'RestartError', 'Restart frame # can only be 0'
		self.boxsize = _amber.ReadRestartFrame( crd, self.natom, self.box, self.vel, self.frameptr(frame), self.traj)
	    ## why return None if boxsize is None?
	    if self.boxsize == None:
		return None

	    newcrd =  numpy.resize(crd, (self.natom,3))
	    del crd

	return newcrd

    def WriteFrame(self, natom, frame, fd, atype='traj', writebox=None):
	if atype == None:
	    atype = self.type

	if atype == 'traj':
	    _amber.WriteTrajectoryFrame(natom, frame, fd)
	if atype == 'rest':
	    _amber.WriteRestartFrame(natom, frame, fd)


	if writebox or (writebox == None and self.prm['box']):
	    if self.prm['box']:
		fd.write("%8.3f%8.3f%8.3f\n" % (self.boxsize[0],self.boxsize[1],self.boxsize[2]))

