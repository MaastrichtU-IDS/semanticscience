# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: RmsdMap.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter, Pmw
from chimera.baseDialog import ModelessDialog, AskYesNoDialog
from prefs import prefs, RMSD_MIN, RMSD_MAX, RMSD_AUTOCOLOR
from chimera import UserError

class RmsdStarter(ModelessDialog):
	title = "Get RMSD Map Parameters"
	help = "ContributedSoftware/movie/movie.html#rmsd"

	def __init__(self, movie):
		self.movie = movie
		movie.subdialogs.append(self)
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		from chimera.tkoptions import IntOption, BooleanOption, \
							FloatOption
		Tkinter.Label(parent, text="Create RMSD map of trajectory "
			"against itself", relief="ridge", bd=4).grid(row=0,
			column=0, columnspan=2, sticky="ew")

		startFrame = self.movie.startFrame
		endFrame = self.movie.endFrame
		self.startFrame = IntOption(parent, 1, "Starting frame",
			startFrame, None, min=startFrame, max=endFrame, width=6)

		numFrames = endFrame - startFrame + 1
		defStride = 1 + int(numFrames/300)
		self.stride = IntOption(parent, 2, "Step size", defStride,
			None, min=1, max=numFrames, width=3)

		self.endFrame = IntOption(parent, 3, "Ending frame", endFrame,
			None, min=startFrame, max=endFrame, width=6)

		self.minRmsd = FloatOption(parent, 4, "Lower RMSD threshold"
				" (white)", prefs[RMSD_MIN], None, width=6)
		self.maxRmsd = FloatOption(parent, 5, "Upper RMSD threshold"
				" (black)", prefs[RMSD_MAX], None, width=6)

		self.useSel = BooleanOption(parent, 6, "Restrict map to "
				"current selection, if any", True, None)

		self.ignoreBulk = BooleanOption(parent, 7, "Ignore solvent/"
							"ions", True, None)
		self.ignoreHyds = BooleanOption(parent, 8, "Ignore hydrogens",
							True, None)
		self.recolor = BooleanOption(parent, 9, "Auto-recolor for"
				" contrast", prefs[RMSD_AUTOCOLOR], None)
	def Apply(self):
		startFrame = self.startFrame.get()
		stride = self.stride.get()
		if (len(self.movie.ensemble) - (startFrame-1)) / stride > 1000:
			dlg = AskYesNoDialog("RMSD map will be %d pixels wide"
				" and tall. Okay?")
			if dlg.run(self.uiMaster()) == "no":
				self.enter()
				return
		endFrame = self.endFrame.get()
		if endFrame <= startFrame:
			self.enter()
			raise UserError("Start frame must be less"
							" than end frame")
		if startFrame < self.movie.startFrame \
		or endFrame > self.movie.endFrame:
			self.enter()
			raise UserError("Start or end frame outside"
							" of trajectory")
		prefs[RMSD_MIN] = self.minRmsd.get()
		prefs[RMSD_MAX] = self.maxRmsd.get()
		prefs[RMSD_AUTOCOLOR] = self.recolor.get()
		RmsdMapDialog(self.movie, startFrame, self.stride.get(),
			endFrame, self.useSel.get(), prefs[RMSD_MIN],
			prefs[RMSD_MAX], self.ignoreBulk.get(),
			self.ignoreHyds.get(), prefs[RMSD_AUTOCOLOR])

class RmsdMapDialog(ModelessDialog):
	oneshot = True
	provideStatus = True
	buttons = ("Close",)
	help = "ContributedSoftware/movie/movie.html#rmsd"

	titleFmt = "%g-%g RMSD Map"

	def __init__(self, movie, startFrame, stride, endFrame, useSel, minRmsd,
				maxRmsd, ignoreBulk, ignoreHyds, recolor):
		self.movie = movie
		self.movie.subdialogs.append(self)
		self.startFrame = startFrame
		self.stride = stride
		self.endFrame = endFrame
		self.useSel = useSel
		self.minRmsd = minRmsd
		self.maxRmsd = maxRmsd
		self.ignoreBulk = ignoreBulk
		self.ignoreHyds = ignoreHyds
		self.recolor = recolor
		self.title = self.titleFmt % (minRmsd, maxRmsd)
		ModelessDialog.__init__(self)

	def Close(self):
		if self._computing:
			self._abort = True
			return
		self.movie.subdialogs.remove(self)
		while self.dependentDialogs:
			self.dependentDialogs.Close()
		ModelessDialog.Close(self)

	def destroy(self):
		while self.dependentDialogs:
			self.dependentDialogs[0].Close()
		# calling ModelessDialog.Close causes recursion
		ModelessDialog.destroy(self)

	def fillInUI(self, parent):
		from chimera.match import matchPositions
		from chimera import numpyArrayFromAtoms
		from chimera import selection, UserError

		self._computing = False
		top = parent.winfo_toplevel()
		menuBar = Tkinter.Menu(top)
		top.config(menu=menuBar)

		self.dependentDialogs = []
		rmsdMenu = Tkinter.Menu(menuBar)
		menuBar.add_cascade(label="RMSD", menu=rmsdMenu)
		rmsdMenu.add_command(label="Change thresholds...",
					command=self.launchRmsdBoundsDialog)

		numFrames = self.endFrame - self.startFrame + 1
		scale1size = numFrames / self.stride
		if scale1size < 200:
			scale = int(1 + 200 / scale1size)
		else:
			scale = 1
		# load needed coord sets...
		for frameNum in range(self.startFrame, self.endFrame+1,
								self.stride):
			if not self.movie.findCoordSet(frameNum):
				self.status("loading frame %d" % frameNum)
				self.movie._LoadFrame(frameNum,
							makeCurrent=False)

		self.widgets = []
		width = max(len(str(self.endFrame)), 6)
		for i in range(2):
			entryFrame = Tkinter.Frame(parent)
			entryFrame.grid(row=1, column=i)
			entry = Pmw.EntryField(entryFrame, labelpos='w',
					entry_width=width, label_text="Frame",
					validate='numeric')
			entry.configure(command=lambda ent=entry:
							self.entryCB(ent))
			entry.grid(row=0, column=0)
			self.widgets.append(entry)
			goBut = Tkinter.Button(entryFrame, text="Go",
				padx=0, pady=0,
				command=lambda ent=entry: self.entryCB(ent))
			goBut.grid(row=0, column=1)
			self.widgets.append(goBut)
		self.widgets[0].insert(0, "Click")
		self.widgets[2].insert(0, "on map")
		for widget in self.widgets:
			if isinstance(widget, Pmw.EntryField):
				widget = widget.component('entry')
			widget.config(state='disabled')

		size = scale1size * scale
		self.scrCanvas = Pmw.ScrolledCanvas(parent, canvas_bg="blue",
			canvas_width=size, canvas_height=size, borderframe=True)
		self.scrCanvas.grid(row=0, column=0, columnspan=2,
								sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)

		# compute RMSD/image canvas
		from analysis import analysisAtoms
		try:
			atoms = analysisAtoms(self.movie, self.useSel,
					self.ignoreBulk, self.ignoreHyds)
		except UserError:
			self.Close()
			raise

		self.buttonWidgets['Close'].configure(text="Abort")
		self.rects = {}
		numpyArrays = {}
		if self.recolor:
			rmsds = []
		minRmsd = maxRmsd = None
		for step1, frame1 in enumerate(range(self.startFrame,
						self.endFrame+1, self.stride)):
			self.status("compute/show RMSDs for frame %d" % frame1)
			try:
				na1 = numpyArrays[frame1]
			except KeyError:
				na1 = numpyArrayFromAtoms(atoms,
					self.movie.findCoordSet(frame1))
				numpyArrays[frame1] = na1
			canvas = self.scrCanvas.component('canvas')
			for step2, frame2 in enumerate(range(frame1,
						self.endFrame+1, self.stride)):
				try:
					na2 = numpyArrays[frame2]
				except KeyError:
					na2 = numpyArrayFromAtoms(atoms,
						self.movie.findCoordSet(frame2))
					numpyArrays[frame2] = na2
				rmsd = matchPositions(na1, na2)[1]
				if self.recolor:
					rmsds.append(rmsd)
				color = self.tkRmsdColor(rmsd)
				rect1 = canvas.create_rectangle(step1*scale,
					(step1+step2)*scale, (step1+1)*scale,
					(step1+step2+1)*scale, fill=color,
					outline="")
				self.rects[rect1] = (frame1, frame2, rmsd)
				rect2 = canvas.create_rectangle(
					(step1+step2)*scale, step1*scale,
					(step1+step2+1)*scale, (step1+1)*scale,
					fill=color, outline="")
				self.rects[rect2] = (frame2, frame1, rmsd)
				if frame1 != frame2:
					if minRmsd is None:
						minRmsd = maxRmsd = rmsd
					elif rmsd < minRmsd:
						minRmsd = rmsd
					elif rmsd > maxRmsd:
						maxRmsd = rmsd

			if step1 == 0:
				self.scrCanvas.resizescrollregion()
			self._computing = True
			self._abort = False
			canvas.update() # show each line and allow quit
			self._computing = False
			if self._abort:
				canvas.after_idle(self.Close)
				return
		self.buttonWidgets['Close'].configure(text="Close")
		if self.recolor:
			self.status("Calculating recoloring thresholds\n")
			rmsds.sort()
			newMin = float("%.1f" % rmsds[int(len(rmsds)/3)])
			newMax = float("%.1f" % rmsds[int(2*len(rmsds)/3)])
			if newMin == newMax:
				if newMin > 0:
					newMin -= 0.1
				else:
					newMax += 0.1
			self.newMinMax(newMin, newMax)
		canvas.bind("<Motion>", self.mouseOverCB)
		canvas.bind("<Button-1>", self.mouseClickCB)
		self.status("Calculated RMSD varies from %.3f to %.3f\n"
						% (minRmsd, maxRmsd), log=True)

	def entryCB(self, entry):
		self.movie.currentFrame.set(entry.get())
		self.movie.LoadFrame()

	def getRectFromEvent(self, event):
		objs = self.scrCanvas.find_closest(event.x, event.y)
		for obj in objs:
			if obj in self.rects:
				return obj
		return None

	def launchRmsdBoundsDialog(self):
		self.dependentDialogs.append(BoundsChangeDialog(self))

	def mouseClickCB(self, event):
		rect = self.getRectFromEvent(event)
		if not rect:
			return
		for i in range(2):
			self.widgets[i*2].component('entry').configure(
								state='normal')
			self.widgets[i*2+1].configure(state='normal')
			self.widgets[i*2].setvalue(str(self.rects[rect][i]))

	def mouseOverCB(self, event):
		rect = self.getRectFromEvent(event)
		if rect:
			self.status("frames %d/%d, RMSD: %.3f"
							% self.rects[rect])
		else:
			self.status("")

	def newMinMax(self, newMin, newMax):
		prefs[RMSD_MIN] = self.minRmsd = newMin
		prefs[RMSD_MAX] = self.maxRmsd = newMax
		canvas = self.scrCanvas.component("canvas")
		self.status("recoloring map...", blankAfter=0)
		for rect, rectInfo in self.rects.items():
			canvas.itemconfigure(rect,
					fill=self.tkRmsdColor(rectInfo[-1]))
		self.status("map recolored")
		self.uiMaster().winfo_toplevel().title(self.titleFmt
							% (newMin, newMax))

	def tkRmsdColor(self, rmsd):
		if rmsd <= self.minRmsd:
			return 'white'
		if rmsd >= self.maxRmsd:
			return 'black'
		return '#' + ('%02x' % (255 - int(256 * (rmsd - self.minRmsd)
					/ (self.maxRmsd - self.minRmsd)))) * 3

class BoundsChangeDialog(ModelessDialog):
	title = "Change RMSD Thresholds"
	oneshot = True
	default = "OK"
	help = "ContributedSoftware/movie/movie.html#changethresh"

	def __init__(self, rmsdDialog):
		self.rmsdDialog = rmsdDialog
		ModelessDialog.__init__(self)

	def Apply(self):
		prefs[RMSD_MIN] = self.newMin.get()
		prefs[RMSD_MAX] = self.newMax.get()
		self.rmsdDialog.newMinMax(prefs[RMSD_MIN], prefs[RMSD_MAX])

	def Close(self):
		self.rmsdDialog.dependentDialogs.remove(self)
		ModelessDialog.Close(self)

	def fillInUI(self, parent):
		from chimera.tkoptions import FloatOption
		self.newMin = FloatOption(parent, 0,
					"New lower RMSD threshold (white)",
					prefs[RMSD_MIN], None)
		self.newMax = FloatOption(parent, 1,
					"New upper RMSD threshold (black)",
					prefs[RMSD_MAX], None)
