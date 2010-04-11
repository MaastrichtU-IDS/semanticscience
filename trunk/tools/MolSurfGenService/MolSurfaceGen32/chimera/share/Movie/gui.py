#!/usr/local/chimera/bin/chimera

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import sys
import os
import chimera
import Tkinter, Pmw
import chimera.tkgui
import Movie
import Trajectory
from Trajectory import EnsembleLoader, NoFrameError
from chimera import replyobj, Point
from prefs import prefs, SCRIPT_PYTHON, SCRIPT_CHIMERA, SCRIPT_TYPE, \
				DICT_NAME, FRAME_TEXT, ZERO_PAD

from PIL import Image
from PIL import ImageTk
Image.preinit()
from PIL import PngImagePlugin

rgb = 0,0,0
def GenImage(filename, tk):
	image = Image.open(filename)
	i = Image.new("RGB", image.size, rgb)
	i.paste(image)
	imtk = ImageTk.PhotoImage(i, master=tk)
	return imtk

triggerName = 'new frame'

from chimera.baseDialog import ModelessDialog
class MovieDialog(ModelessDialog):
	help = "ContributedSoftware/movie/movie.html#viewing"
	buttons = ("Hide", "Quit")
	provideStatus = True

	def __init__(self, ensemble, **kw):
		self.title = "MD Movie: %s" % ensemble.name
		self.ensemble = ensemble
		self.model = Trajectory.Ensemble(self.ensemble)
		self.model.CreateMolecule()
		endFrame = ensemble.endFrame
		if endFrame == "pipe":
			fn = 1
			while True:
				replyobj.status("Loading trajectory from pipe:"
					" frame %d\n" % fn)
				try:
					self.model.LoadFrame(fn,
							makeCurrent=False)
				except NoFrameError:
					break
				fn += 1
			replyobj.status("Loading trajectory from pipe: done\n")
			endFrame = fn-1
		if ensemble.startFrame == None:
			self.startFrame = 1
		else:
			self.startFrame = ensemble.startFrame
			if self.startFrame > len(ensemble):
				replyobj.warning("Start frame > number of"
					" trajectory frames; changing start"
					" frame to 1\n")
				self.startFrame = 1
		if endFrame == None:
			self.endFrame = len(ensemble)
		else:
			self.endFrame = endFrame
			if self.endFrame > len(ensemble):
				replyobj.warning("End frame > number of"
					" trajectory frames; changing end"
					" frame to last frame\n")
				self.endFrame = len(ensemble)
		self.molTrigID = chimera.triggers.addHandler("Molecule",
							self._molTrigCB, None)
		self.openOpts = kw
		self._inTriggerCB = False
		ModelessDialog.__init__(self)
		del self.openOpts
		chimera.extension.manager.registerInstance(self)

	def fillInUI(self, parent):
		parent.winfo_toplevel().protocol('WM_DELETE_WINDOW', self.Quit)

		self.movieRunning = 0
		self.direction = 1
		self.trigger = None
		self.holdingSteady = None
		self.recording = False
		self.transforms = {}
        
		## load the trajectory
		self.currentFrame = Tkinter.IntVar(parent)

		self.currentFrame.set(self.startFrame)

		## load the first frame
		self.script = None
		self.LoadFrame()

		## add the model to chimera
		self.model.AddMolecule(**self.openOpts)

		## set up the icons
		moviepath = Movie.__path__[0]

		row1Frame = Tkinter.Frame(parent)
		row1Frame.grid(row=1, column=0, sticky='ew')
		parent.columnconfigure(0, weight=1)

		butFrame = Tkinter.Frame(row1Frame)
		butFrame.grid(row=0, column=0)
		row1Frame.columnconfigure(0, weight=1)

		icon = os.path.join(moviepath, 'Icons/image_reverse.png')
		imtk = GenImage(icon, parent)
		button = Tkinter.Button(butFrame,
			command=self.startMovieReverseCallback, image=imtk)
		button._image=imtk
		button.grid(row=0, column=0)

		icon = os.path.join(moviepath, 'Icons/image_previous.png')
		imtk = GenImage(icon, parent)
		button = Tkinter.Button(butFrame,
				command=self.minusCallback, image=imtk)
		button._image=imtk
		button.grid(row=0, column=1)

		icon = os.path.join(moviepath, 'Icons/image_pause.png')
		imtk = GenImage(icon, parent)
		button = Tkinter.Button(butFrame,
				command=self.stopMovieCallback, image=imtk)
		button._image=imtk
		button.grid(row=0, column=2)

		icon = os.path.join(moviepath, 'Icons/image_next.png')
		imtk = GenImage(icon, parent)
		button = Tkinter.Button(butFrame,
				command=self.plusCallback, image=imtk)
		button._image=imtk
		button.grid(row=0, column=3)

		icon = os.path.join(moviepath, 'Icons/image_play.png')
		imtk = GenImage(icon, parent)
		button = Tkinter.Button(butFrame,
			command=self.startMovieForwardCallback, image=imtk)
		button._image=imtk
		button.grid(row=0, column=4)

		self.loopVar = Tkinter.IntVar(parent)
		self.loopVar.set(True)
		check = Tkinter.Checkbutton(row1Frame, text="Loop",
						variable=self.loopVar)
		check.grid(row=0, column=1)
		row1Frame.columnconfigure(1, weight=1)


		row2Frame = Tkinter.Frame(parent)
		row2Frame.grid(row=2, column=0, sticky='ew')

		Tkinter.Label(row2Frame, text="Playback speed:").grid(
							row=0, column=0)

		scrollFrame = Tkinter.Frame(row2Frame, bd=1, bg='black')
		scrollFrame.grid(row=0, column=1, sticky='ew', padx=2)
		row2Frame.columnconfigure(1, weight=1)

		Tkinter.Label(scrollFrame, text="slower").grid(
						row=0, column=0, sticky="nsew")
		Tkinter.Label(scrollFrame, text="faster").grid(
						row=0, column=2, sticky="nsew")

		self.inDelay = False
		self.playbackDelay = 0.0
		scale = Tkinter.Scale(scrollFrame, from_=1.0,
			to_=0.0, command=lambda sp: setattr(self,
			'playbackDelay', float(sp)), orient="horizontal",
			resolution=0.01, showvalue=0)
		scale.set(self.playbackDelay)
		scale.grid(row=0, column=1, sticky='ew')
		scrollFrame.columnconfigure(1, weight=1)

		top = parent.winfo_toplevel()
		self.menuBar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=self.menuBar)

		row3Frame = Tkinter.Frame(parent)
		row3Frame.grid(row=3, column=0, sticky='ew')

		self.frameEntry = Pmw.EntryField(row3Frame, validate='integer',
				entry_justify='right', labelpos='w',
				label_text="Frame", command=self.LoadFrame,
				entry_textvariable=self.currentFrame,
				entry_width=len(str(len(self.ensemble))))
		self.frameEntry.grid(row=0, column=0, sticky='e')
		row3Frame.columnconfigure(0, weight=1)

		self.sizeLabel = Tkinter.Label(row3Frame, text="of %d"
							% len(self.ensemble))
		self.sizeLabel.grid(row=0, column=1, sticky='w')

		self.step = 1
		self.stepEntry = Pmw.EntryField(row3Frame,
			command=self.setStep, labelpos='w',
			validate={'min': 1, 'validator': 'numeric'},
			value=str(self.step), label_text="Step size",
			entry_width=max(1, len("%d" % len(self.ensemble))-1))
		self.stepEntry.grid(row=0, column=2)
		row3Frame.columnconfigure(2, weight=1)
			
		self.fileMenu = Tkinter.Menu(self.menuBar)
		self.menuBar.add_cascade(label="File", menu=self.fileMenu)
		def showWritePdbDialog():
			from ModelPanel.writePDBdialog import WritePDBdialog
			from chimera import dialogs
			dialogs.display(WritePDBdialog.name).configure(
							[self.model._mol])
		self.fileMenu.add_command(label="Save PDB...",
						command=showWritePdbDialog)

		from RecorderDialog import RecorderDialog
		self.recorderDialog = None
		self.fileMenu.add_command(label="Record movie...",
			command=lambda: (self.recorderDialog or
			setattr(self, 'recorderDialog', RecorderDialog(self)))
			and self.recorderDialog.enter())

		self.addTrajDialog = None
		if hasattr(self.ensemble, 'addTraj') \
		and hasattr(self.ensemble, 'AddTrajKw'):
			cmd = lambda: (self.addTrajDialog or setattr(self,
					'addTrajDialog', AddTrajDialog(self))
					) and self.addTrajDialog.enter()
			state = 'normal'
		else:
			cmd = None
			state = 'disabled'
		self.fileMenu.add_command(label="Load Additional Frames...",
						state=state, command=cmd)

		self.actionsMenu = Tkinter.Menu(self.menuBar)
		self.menuBar.add_cascade(label="Actions", menu=self.actionsMenu)
		self.actionsMenu.add_command(label="Hold selection steady",
						command=self.holdSteadyCB)
		self.stopHoldingLabel = "Stop holding steady"
		self.actionsMenu.add_command(label=self.stopHoldingLabel,
				command=self.stopHoldingCB, state='disabled')

		self.perFrameMenu = Tkinter.Menu(self.menuBar)
		self.menuBar.add_cascade(label="Per-Frame",
							menu=self.perFrameMenu)
		self.subdialogs = [] # list to destroy on Quit
		self.scriptDialog = None
		self.perFrameMenu.add_command(label="Define script...",
			command=lambda: (self.scriptDialog or
			setattr(self, 'scriptDialog', ScriptDialog(self))) and
			self.scriptDialog.enter())
		self.perFrameMenu.add_command(label="Stop running script",
				command=self.stopScript, state="disabled")

		analysisMenu = Tkinter.Menu(self.menuBar)
		self.menuBar.add_cascade(label="Analysis", menu=analysisMenu)
		from VolumeDialog import VolumeDialog
		self.volumeDialog = None
		analysisMenu.add_command(label="Calculate occupancy...",
			command=lambda: (self.volumeDialog or
			setattr(self, 'volumeDialog', VolumeDialog(self))) and
			self.volumeDialog.enter())
		from Cluster import ClusterStarter
		self.clusterDialog = None
		analysisMenu.add_command(label="Cluster...",
			command=lambda: (self.clusterDialog or
			setattr(self, 'clusterDialog', ClusterStarter(self)))
			and self.clusterDialog.enter())
		from RmsdMap import RmsdStarter
		self.rmsdDialog = None
		analysisMenu.add_command(label="RMSD map...",
			command=lambda: (self.rmsdDialog or
			setattr(self, 'rmsdDialog', RmsdStarter(self))) and
			self.rmsdDialog.enter())

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(self.menuBar, parent, row = 0)

		if self.ensemble.startFrame in (None, 0, 1) \
		and self.ensemble.endFrame == None:
			self.status("Using all trajectory frames")
		else:
			self.status("Restricted frame range: %d to %d"
				% (self.startFrame, self.endFrame))
	def emHide(self):
		"""extension manager method"""
		ModelessDialog.Cancel(self)
	Hide = emHide

	def emName(self):
		"""extension manager method"""
		return "MD Movie - %s" % self.ensemble.name

	def emQuit(self, deleteMolecule=True):
		"""extension manager method"""
		if self.trigger is not None:
			chimera.triggers.deleteHandler(triggerName,
							self.trigger)
		if self.molTrigID is not None:
			chimera.triggers.deleteHandler("Molecule",
							self.molTrigID)
		if self.recording:
			self.abortRecording()
		if deleteMolecule:
			mol = self.model.Molecule()
			assocSurfs = chimera.openModels.list(mol.id, mol.subid,
				modelTypes=[chimera.MSMSModel])
			if assocSurfs:
				chimera.openModels.close(assocSurfs)
			self.model.DeleteMolecule()
		self.Cancel()
		chimera.extension.manager.deregisterInstance(self)
		for d in self.subdialogs:
			d.destroy()
		self.destroy()
	Quit = emQuit

	def emRaise(self):
		"""extension manager method"""
		self.enter()

	def abortRecording(self):
		if not self.recording:
			return
		from chimera import runCommand
		self.recording = False
		runCommand("movie stop; movie reset")
		self.status("Animation recording aborted")

	def addTrajFile(self, trajFile):
		self.ensemble.addTraj(trajFile)
		self.endFrame = len(self.ensemble)
		self.sizeLabel.configure(text="of %d" % len(self.ensemble))

	def computeVolume(self, atoms, startFrame=None, endFrame=None,
			bound=None, volumeName=None, step=1, spacing=0.5):
		# load and process frames
		if startFrame is None:
			startFrame = self.startFrame
		if endFrame is None:
			endFrame = self.endFrame
		if bound is not None:
			from _closepoints import find_close_points, BOXES_METHOD
		from Matrix import xform_matrix
		if self.holdingSteady:
			steadyAtoms, steadySel, steadyCS, inverse = \
							self.holdingSteady
			# all the above used later...
			inverse = xform_matrix(inverse)

		gridData = {}
		from math import floor
		from numpy import array, float32
		from _contour import affine_transform_vertices
		for fn in range(startFrame, endFrame+1, step):
			cs = self.findCoordSet(fn)
			if not cs:
				self.status("Loading frame %d" % fn)
				self._LoadFrame(fn, makeCurrent=False)
				cs = self.findCoordSet(fn)

			self.status("Processing frame %d" % fn)
			pts = array([a.coord(cs) for a in atoms], float32)
			if self.holdingSteady:
				if bound is not None:
					steadyPoints = array([a.coord(cs)
						for a in steadyAtoms], float32)
					closeIndices = find_close_points(
						BOXES_METHOD, steadyPoints,
						#otherPoints, bound)[1]
						pts, bound)[1]
					pts = pts[closeIndices]
				try:
					xf, inv = self.transforms[fn]
				except KeyError:
					xf, inv = self.steadyXform(cs=cs)
					self.transforms[fn] = (xf, inv)
				xf = xform_matrix(xf)
				affine_transform_vertices(pts, xf)
				affine_transform_vertices(pts, inverse)
			# add a half-voxel since volume positions are
			# considered to be at the center of their voxel
			from numpy import floor, zeros
			pts = floor(pts/spacing + 0.5).astype(int)
			for pt in pts:
				center = tuple(pt)
				gridData[center] = gridData.get(center, 0) + 1

		# generate volume
		self.status("Generating volume")
		axisData = zip(*tuple(gridData.keys()))
		minXyz = [min(ad) for ad in axisData]
		maxXyz = [max(ad) for ad in axisData]
		# allow for zero-padding on both ends
		dims = [maxXyz[axis] - minXyz[axis] + 3 for axis in range(3)]
		from numpy import zeros, transpose
		volume = zeros(dims, int)
		for index, val in gridData.items():
			adjIndex = tuple([index[i] - minXyz[i] + 1
							for i in range(3)])
			volume[adjIndex] = val
		from VolumeData import Array_Grid_Data
		gd = Array_Grid_Data(volume.transpose(),
					# the "cushion of zeros" means d-1...
					[(d-1) * spacing for d in minXyz],
					[spacing] * 3)
		if volumeName is None:
			volumeName = self.ensemble.name
		gd.name = volumeName

		# show volume
		self.status("Showing volume")
		import VolumeViewer
		dataRegion = VolumeViewer.volume_from_grid_data(gd)
		vd = VolumeViewer.volumedialog.volume_dialog(create=True)
		vd.message("Volume can be saved from File menu")

		self.status("Volume shown")

	def _endRecording(self, *args):
		from Midas import MidasError
		try:
			from chimera import runCommand
			runCommand("movie stop")
			self.status("Compiling frames into animation",
								blankAfter=5)
			runCommand("movie encode " + self.encodeArgs)
		except:
			self.status("Error stopping/encoding movie",
								color="red")
			from chimera.replyobj import reportException
			reportException("Error stopping/encoding movie")
		from chimera.triggerSet import ONESHOT
		return ONESHOT

	def findCoordSet(self, csNum):
		if self.model.findCoordSet(0):
			return self.model.findCoordSet(csNum-1)
		return self.model.findCoordSet(csNum)

	def holdSteadyCB(self):
		"""'hold steady' menu callback"""
		from chimera.actions import selAtoms
		from chimera.selection import ItemizedSelection
		atoms = selAtoms()
		if not atoms:
			replyobj.error("No atoms selected\n")
			return
		self.status("Holding %d atoms steady" % len(atoms))
		steadySel = ItemizedSelection(selChangedCB=self._steadySelCB)
		steadySel.add(atoms)
		identity = chimera.Xform.identity()
		curFrame = self.currentFrame.get()
		cs = self.model.activeCoordSet
		self.holdingSteady = (atoms, steadySel, cs, identity)
		self.transforms = { curFrame: (identity, identity) }
		self.actionsMenu.entryconfigure(self.stopHoldingLabel,
							state='normal')
		if self.volumeDialog:
			# clear "no atoms held steady" error
			self.volumeDialog.status("")

	def LoadFrame(self):
		from chimera import UserError
		if hasattr(self, 'frameEntry') and not self.frameEntry.valid():
			raise UserError("Bad frame number text: %s" %
					self.frameEntry.getvalue())
		currentFrame = self.currentFrame.get()
		if currentFrame < self.startFrame \
		or currentFrame > self.endFrame:
			self.currentFrame.set(self.startFrame)
			raise UserError("Frame %d out of range!" % currentFrame)
		self._LoadFrame(currentFrame, makeCurrent=True)
		if self.holdingSteady:
			atoms, steadySel, steadyCS, inverse = self.holdingSteady
			baseXform = self.model.openState.xform
			baseXform.multiply(inverse)
			try:
				xform, inverse = self.transforms[currentFrame]
			except:
				xform, inverse = self.steadyXform()
				self.transforms[currentFrame] = (xform, inverse)
			baseXform.multiply(xform)
			self.model.openState.xform = baseXform
			self.holdingSteady = (atoms, steadySel, steadyCS,
								inverse)
		if self.script:
			if self.scriptType == SCRIPT_PYTHON:
				scriptGlobals = {
					'chimera': chimera
				}
				if self.frameSubst \
				and self.frameSubst.isalnum():
					scriptGlobals[self.frameSubst] = {
						'mol': self.model._mol,
						'startFrame': self.startFrame,
						'endFrame': self.endFrame,
						'frame': self.currentFrame.get()
					}
			else:
				from Midas.midas_text import processCommandFile
				# activate lines that begin with
				# "#<currentframe>:"
				processedLines = []
				curFrame = self.currentFrame.get()
				sigil = "#%d:" % curFrame
				for line in self.script.splitlines(True):
					if line.startswith(sigil):
						processedLines.append(
							line[len(sigil):])
					else:
						processedLines.append(line)
				script = "".join(processedLines)
				if self.frameSubst \
				  and not self.frameSubst.isspace():
					fn = str(curFrame)
					if self.zeroPad:
						lf = len(self.ensemble)
						digits = len(str(lf))
						fn = "0" * (digits-len(fn)) + fn
					script = script.replace(
							self.frameSubst, fn)
			try:
				if self.scriptType == SCRIPT_PYTHON:
					exec self.script in scriptGlobals, {}
				else:
					processCommandFile(script,
							emulateRead=True,
							usingString=True)
			except:
				from chimera.replyobj import reportException
				reportException("Problem in per-frame script")
				self.stopMovieCallback()
		if self.recording \
		and currentFrame + self.recordStep > self.recordEnd:
			self.recording = False
			self.stopMovieCallback()
			# stop recording after next frame appears...
			chimera.triggers.addHandler('new frame',
						self._endRecording, None)
        
	def _LoadFrame(self, frameNum, makeCurrent=True):
		if self.model.findCoordSet(0):
			self.model.LoadFrame(frameNum-1,makeCurrent=makeCurrent)
		else:
			self.model.LoadFrame(frameNum, makeCurrent=makeCurrent)

	def _molTrigCB(self, trigName, myData, trigData):
		if self.model._mol in trigData.deleted:
			self.emQuit(deleteMolecule=False)

	def recordAnimation(self, startFrame=None, endFrame=None,
				step=1, recordArgs="", encodeArgs=""):
		if startFrame is None:
			startFrame = self.startFrame
		if endFrame is None:
			endFrame = self.endFrame

		if self.recording:
			self.status("Already recording an animation",
								color="red")
			return

		self.stopMovieCallback()

		self.currentFrame.set(startFrame)
		self.recordEnd = endFrame
		self.recordStep = step
		self.encodeArgs = encodeArgs
		self.LoadFrame()
		self.recording = True
		from chimera import runCommand
		self.status("Recording animation...", blankAfter=0)
		runCommand("movie record " + recordArgs)
		chimera.triggers.addHandler("post-frame", self._startAnimation,
								None)

	def setStep(self):
		if self.stepEntry.valid():
			self.step = int(self.stepEntry.getvalue())

	def _surfaceCheck(self):
		if getattr(self, "_surfaceOkayed", False):
			return True
		mol = self.model.Molecule()
		assocSurfs = chimera.openModels.list(mol.id, mol.subid,
			modelTypes=[chimera.MSMSModel])
		if not assocSurfs:
			return True
		from chimera.baseDialog import AskYesNoDialog
		answer = AskYesNoDialog("A surface model exists for this"
			" trajectory.\nThe surface will be recalculated for each frame"
			" which will slow playback significantly.\nYou may want to close"
			" the surface before playing the trajectory.\nContinue anyway?"
			).run(self.uiMaster())
		self._surfaceOkayed = answer == "yes"
		return self._surfaceOkayed

	def _startAnimation(self, *args):
		self.startMovieForwardCallback()
		from chimera.triggerSet import ONESHOT
		return ONESHOT

	def _steadySelCB(self):
		steadyAtoms, steadySel, steadyCoordSet, inverse = \
							self.holdingSteady
		newAtoms = steadySel.atoms()
		if not newAtoms:
			self.stopHoldingCB()
			return
		self.holdingSteady = (newAtoms, steadySel, steadyCoordSet,
								inverse)
		
	def steadyXform(self, cs=None):
		steadyAtoms, steadySel, steadyCoordSet, inverse = \
							self.holdingSteady
		from chimera import match
		if cs is None:
			cs = self.model.activeCoordSet
		xform = match.matchAtoms(steadyAtoms, steadyAtoms,
						steadyCoordSet, cs)[0]
		return xform, xform.inverse()

	def stopHoldingCB(self):
		"""'stop holding steady' menu callback"""
		self.holdingSteady = None
		self.transforms = None
		self.status("")
		self.actionsMenu.entryconfigure(self.stopHoldingLabel,
							state='disabled')

	def stopScript(self):
		self.script = None
		self.perFrameMenu.entryconfigure("Stop *", state='disabled')

	def UpdateMovie(self, triggerName, closure, triggerData):
		if not self.movieRunning:
			return
		if self.inDelay:
			return
		if self._inTriggerCB:
			return
		self._inTriggerCB = True
		if self.playbackDelay:
			self.uiMaster().after(int(1000 * self.playbackDelay),
							self.advanceFrame)
			self.inDelay = True
		else:
			self.advanceFrame()
		self._inTriggerCB = False

	def advanceFrame(self):
		self.inDelay = False
		if self.recording:
			step = self.recordStep
			direction = 1
		else:
			step = self.step
			direction = self.direction
		curFrame = self.currentFrame.get()
		self.currentFrame.set(curFrame + step * direction)
		loop = False
		if self.currentFrame.get() >= self.endFrame + 1:
			loop = True
			self.currentFrame.set(self.startFrame)
		elif self.currentFrame.get() <= self.startFrame - 1:
			loop = True
			self.currentFrame.set(self.endFrame)
		if loop and not self.loopVar.get():
			self.currentFrame.set(curFrame)
			self.stopMovieCallback()
			return

		self.LoadFrame()

	def setScript(self, script, scriptType, zeroPad=False, frameSubst=None):
		self.script = script
		self.scriptType = scriptType
		self.zeroPad = zeroPad
		self.frameSubst = frameSubst
		self.LoadFrame()

		self.perFrameMenu.entryconfigure("Stop *", state='normal')

	def startMovieReverseCallback(self):
		if not self._surfaceCheck():
			return
		if self.trigger is not None:
			chimera.triggers.deleteHandler(triggerName,
								self.trigger)
			self.trigger = None
            
		self.movieRunning = 1
		self.direction = -1
		self.trigger = chimera.triggers.addHandler(triggerName,
						self.UpdateMovie, None)
    
	def startMovieForwardCallback(self):
		if not self._surfaceCheck():
			return
		if self.trigger is not None:
			chimera.triggers.deleteHandler(triggerName,
								self.trigger)
			self.trigger = None

		self.movieRunning = 1
		self.direction = 1
		self.trigger = chimera.triggers.addHandler(triggerName,
						self.UpdateMovie, None)

	def stopMovieCallback(self):
		if self.trigger is not None:
			chimera.triggers.deleteHandler(triggerName,
								self.trigger)
			self.trigger = None
            
		self.movieRunning = 0
		self.trigger = None
		if self.recording:
			self.abortRecording()

	def minusCallback(self):
		if self.movieRunning: return
		newFrame = self.currentFrame.get() - self.step
		if newFrame >= self.startFrame:
			loop = False
		else:
			newFrame = self.endFrame
			loop = True
		if loop and not self.loopVar.get():
			return
            
		self.currentFrame.set(newFrame)
		self.LoadFrame()
        
	def plusCallback(self):
		if self.movieRunning: return
		newFrame = self.currentFrame.get() + self.step
		if newFrame <= self.endFrame:
			loop = False
		else:
			newFrame = self.startFrame
			loop = True
		if loop and not self.loopVar.get():
			return

		self.currentFrame.set(newFrame)
		self.LoadFrame()

class ScriptDialog(ModelessDialog):
	
	title = "Per-Frame Commands"
	help = "ContributedSoftware/movie/movie.html#per-frame"
	buttons = ['OK', 'Apply', 'Clear', 'Close']

	def __init__(self, mainDialog, **kw):
		self.mainDialog = mainDialog
		self.mainDialog.subdialogs.append(self)
		ModelessDialog.__init__(self, **kw)

	def fillInUI(self, parent):
		items = [SCRIPT_PYTHON, SCRIPT_CHIMERA]
		if prefs[SCRIPT_TYPE] in items:
			initialitem = prefs[SCRIPT_TYPE]
		else:
			initialitem = SCRIPT_PYTHON
		self.scriptType = Pmw.OptionMenu(parent, items=items,
			command=self._setFrameSubst,
			initialitem=initialitem, labelpos="w",
			label_text="Interpret script as")
		self.scriptType.grid(row=0, column=0, sticky="w")

		self.pythonFrame = Tkinter.Frame(parent)
		self.varField = Pmw.EntryField(self.pythonFrame, labelpos='w',
				label_text="Initialize dictionary",
				entry_width=len(prefs[DICT_NAME]),
				value=prefs[DICT_NAME])
		self.varField.grid(row=0, column=0, sticky='e')
		Tkinter.Label(self.pythonFrame, text="with").grid(row=0,
								column=1)
		tableFrame = Tkinter.Frame(self.pythonFrame,
							relief="solid", bd=1)
		tableFrame.grid(row=0, column=2, sticky='w')
		Tkinter.Label(tableFrame, text="Key", relief="ridge"
			).grid(row=0, column=0, sticky='ew')
		Tkinter.Label(tableFrame, text="Value", relief="ridge"
			).grid(row=0, column=1, sticky='ew')
		for i, kv in enumerate([("frame", "frame number"),
				("mol", "Molecule instance")]):
			Tkinter.Label(tableFrame, text=kv[0]).grid(
				row=i+1, column=0)
			Tkinter.Label(tableFrame, text=kv[1]).grid(
				row=i+1, column=1)
		Tkinter.Label(tableFrame, text="startFrame").grid(row=i+2,
							column=0)
		Tkinter.Label(tableFrame, text="endFrame").grid(row=i+3,
							column=0)
		Tkinter.Label(tableFrame, text="starting/ending\nframe number"
				).grid(row=i+2, rowspan=2, column=1)
			

		self.chimeraFrame = Tkinter.Frame(parent)
		self.textField = Pmw.EntryField(self.chimeraFrame, labelpos='w',
				label_text="Substitute text",
				entry_width=len(prefs[FRAME_TEXT])+1,
				value=prefs[FRAME_TEXT])
		self.textField.grid(row=0, column=0, sticky='e')
		self.entryWidgets = [self.varField, self.textField]
		Tkinter.Label(self.chimeraFrame, text="with frame number").grid(
						row=0, column=1, sticky='w')
		self.zeroPadVar = Tkinter.IntVar(self.chimeraFrame)
		self.zeroPadVar.set(prefs[ZERO_PAD])
		self.zeroPadButton = Tkinter.Checkbutton(self.chimeraFrame,
			text="Use leading zeroes so all frame numbers"
			" are equal length", variable=self.zeroPadVar)
		self.zeroPadButton.grid(row=1, column=0, columnspan=2)
		Tkinter.Label(self.chimeraFrame, text="Commands prefixed with"
				" #N: will be executed at frame N"
				).grid(row=2, column=0, columnspan=2)
		self._setFrameSubst(initialitem)

		grp = Pmw.Group(parent, tag_text="Script")
		grp.grid(row=2, column=0, padx=4, sticky="nsew")
		parent.rowconfigure(2, weight=1)
		parent.columnconfigure(0, weight=1)

		self.scriptText = Tkinter.Text(grp.interior(), spacing1=2,
			height=20, width=80, wrap='word')
		self.scriptText.grid(row=0, column=0, sticky='nsew')
		grp.interior().rowconfigure(0, weight=1)
		grp.interior().columnconfigure(0, weight=1)

		self.readScriptDialog = None
		self.saveDialog = None
		f = Tkinter.Frame(parent)
		f.grid(row=3, column=0, sticky="w")
		from OpenSave import OpenModeless, SaveModeless
		Tkinter.Button(f, command=lambda: (self.readScriptDialog
			or setattr(self, 'readScriptDialog', OpenModeless(
			command=self.readScriptFile, historyID="Movie script")))
			and self.readScriptDialog.enter(), pady=0, text=
			"Insert text file...").grid(row=0, column=0)
		filters = []
		for typeName in items:
			exts = chimera.fileInfo.extensions(typeName)
			if exts:
				extension = exts[0]
			else:
				extension = None
			filters.append((typeName, map(lambda e: "*" + e, exts),
								extension))
		Tkinter.Button(f, command=lambda: (self.saveDialog or
			setattr(self, 'saveDialog', SaveModeless(command=
			self.saveFile, historyID="Movie script", filters=
			filters, defaultFilter=self.scriptType.getvalue())))
			and self.saveDialog.enter(), pady=0, text=
			"Save to file...").grid(row=0, column=1)

	def Apply(self):
		for w in self.entryWidgets:
			w.invoke()
		prefs[SCRIPT_TYPE] = self.scriptType.getvalue()
		prefs[DICT_NAME] = self.varField.getvalue()
		prefs[FRAME_TEXT] = self.textField.getvalue()
		prefs[ZERO_PAD] = self.zeroPadVar.get()
		self.mainDialog.setScript(self.scriptText.get("1.0", 'end'),
				prefs[SCRIPT_TYPE], zeroPad=prefs[ZERO_PAD],
				frameSubst=self.curSubstEntry.getvalue())
		
	def Cancel(self):
		if self.readScriptDialog:
			self.readScriptDialog.Cancel()
		ModelessDialog.Cancel(self)

	def Clear(self):
		self.scriptText.delete("1.0", 'end')

	def destroy(self):
		self.mainDialog = None
		if self.readScriptDialog:
			self.readScriptDialog.destroy()
		if self.saveDialog:
			self.saveDialog.destroy()
		ModelessDialog.destroy(self)

	def readScriptFile(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			f = open(path, "r")
			self.scriptText.insert('insert', f.read())
			f.close()

	def saveFile(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			f = open(path, "w")
			f.write(self.scriptText.get("1.0", 'end'))
			f.close()

	def _setFrameSubst(self, value):
		if value == SCRIPT_PYTHON:
			self.chimeraFrame.grid_forget()
			self.pythonFrame.grid(row=1, column=0)
			self.curSubstEntry = self.varField
		else:
			self.pythonFrame.grid_forget()
			self.chimeraFrame.grid(row=1, column=0)
			self.curSubstEntry = self.textField

from OpenSave import OpenModeless
class AddTrajDialog(OpenModeless):
	
	def __init__(self, mainDialog):
		self.mainDialog = mainDialog
		self.mainDialog.subdialogs.append(self)
		OpenModeless.__init__(self, multiple=False,
					**self.mainDialog.ensemble.AddTrajKw)

	def Apply(self):
		self.mainDialog.addTrajFile(self.getPaths()[0])

