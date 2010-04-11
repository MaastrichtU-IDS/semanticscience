# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: RecorderDialog.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter, Pmw
from OpenSave import SaveModeless
from prefs import prefs, RECORDER_FORMAT, RECORDER_RECORD_ARGS, \
		RECORDER_ENCODE_ARGS, RECORDER_SUPERSAMPLE, RECORDER_RAYTRACE, \
		RECORDER_ROUNDTRIP, RECORDER_SAMPLES
import chimera

class RecorderDialog(SaveModeless):
	title = "Record Animation of Trajectory"
	help = "ContributedSoftware/movie/movie.html#recording"
	default = "Record"

	def __init__(self, movie):
		self.movie = movie
		movie.subdialogs.append(self)
		from MovieRecorder import RecorderGUI
		formats = []
		exts = []
		for fmtInfo in RecorderGUI.formats:
			fmt, ext = fmtInfo[:2]
			formats.append(fmt)
			exts.append("." + ext)
		filters = []
		for i, fmt in enumerate(formats):
			ext = exts[i]
			filters.append((fmt, '*'+ext, ext))
		SaveModeless.__init__(self, clientPos='s', clientSticky='ew',
				defaultFilter=prefs[RECORDER_FORMAT],
				filters=filters, historyID="MD recorder")
	def map(self, e=None):
		from MovieRecorder import checkLicense
		if not checkLicense():
			self.Close()

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		self.clientArea.columnconfigure(1, weight=1)

		startFrame = self.movie.startFrame
		endFrame = self.movie.endFrame
		from chimera.tkoptions import IntOption, BooleanOption, \
						FloatOption, StringOption
		self.startFrame = IntOption(self.clientArea, 0,
					"Starting frame", startFrame, None,
					min=startFrame, max=endFrame, width=6)

		numFrames = endFrame - startFrame + 1
		defStride = 1 + int(numFrames/300)
		self.stride = IntOption(self.clientArea, 2, "Step size",
			defStride, None, min=1, max=numFrames, width=3)

		self.endFrame = IntOption(self.clientArea, 3, "Ending frame",
			endFrame, None, min=startFrame, max=endFrame, width=6)

		self.roundtrip = BooleanOption(self.clientArea, 4, "Encode"
			' forward then backward ("roundtrip")', prefs[
			RECORDER_ROUNDTRIP], None, balloon=
			"Encode the frames in forward and then reverse\n"
			"order so that if the movie is played as a loop\n"
			"the motion seems continuous")

		class FrameQuality(BooleanOption):
			labels = ["screen", "supersampled"]
		self.supersample = FrameQuality(self.clientArea, 5,
			"Frame quality", prefs[RECORDER_SUPERSAMPLE],
			self.supersampleCB, balloon=
			"Whether each frame should be taken as is from\n"
			"the screen (fast) or redrawn at higher quality\n"
			"with several samples per pixel.")

		from chimera.printer import SupersampleOption
		self.samples = SupersampleOption(self.clientArea, 6,
			"Samples", prefs[RECORDER_SAMPLES], None)
		self.supersampleCB()

		self.raytrace = BooleanOption(self.clientArea, 7, "Raytrace"
			" with POV-Ray", prefs[RECORDER_RAYTRACE], None)
			
		def povOptCB():
			from chimera.dialogs import display
			d = display("preferences")
			from chimera.printer import POVRAY_SETUP
			d.setCategoryMenu(POVRAY_SETUP)
		Tkinter.Button(self.clientArea, text="POV-Ray Options", pady=0,
			command=povOptCB).grid(row=8, column=0, columnspan=2)
			
		self.recordArgs = StringOption(self.clientArea, 9,
			"Additional recording options",
			prefs[RECORDER_RECORD_ARGS], None, balloon=
			"Options (other than 'supersample' and 'raytrace')\n"
			"for recording frames as per Chimera's 'movie record'"
			" command")

		self.encodeArgs = StringOption(self.clientArea, 10,
			"Additional encoding options",
			prefs[RECORDER_ENCODE_ARGS], None, balloon=
			"Options (other than 'mformat', 'output', and\n"
			"'roundtrip') for composing the frames into the\n"
			"final animation as per Chimera's 'movie encode'\n"
			"command")
		
		Tkinter.Label(self.clientArea, text=
			"On some computers it may be necessary to make sure"
			" that no\nwindows occlude the main Chimera graphics"
			" window (even\npartially) during non-raytraced movie"
			" recording").grid(row=11, column=0, columnspan=2)

	def Apply(self):
		from chimera import UserError
		startFrame = self.startFrame.get()
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
		path, format = self.getPathsAndTypes()[0]
		prefs[RECORDER_FORMAT] = format
		recordArgs = self.recordArgs.get()
		prefs[RECORDER_RECORD_ARGS] = recordArgs
		encodeArgs = self.encodeArgs.get()
		prefs[RECORDER_ENCODE_ARGS] = encodeArgs
		roundtrip = self.roundtrip.get()
		prefs[RECORDER_ROUNDTRIP] = roundtrip
		supersample = self.supersample.get()
		prefs[RECORDER_SUPERSAMPLE] = supersample
		if supersample:
			samples = self.samples.get()
			prefs[RECORDER_SAMPLES] = samples
			recordArgs = " ".join([recordArgs,
						"supersample", str(samples)])
		raytrace = self.raytrace.get()
		prefs[RECORDER_RAYTRACE] = raytrace
		from MovieRecorder import RecorderGUI
		for ext, fmtInfo in RecorderGUI.command_formats.items():
			if fmtInfo[0] == format:
				break
		recordArgs = " ".join([recordArgs, "raytrace", str(raytrace)])
		reprPath = repr(path)
		if reprPath[0] == 'u':
			# strip unicode indicator
			reprPath = reprPath[1:]
		encodeArgs = " ".join([encodeArgs, "roundtrip", str(roundtrip),
				"mformat", ext, "output", reprPath])
		self.movie.recordAnimation(startFrame=startFrame,
				endFrame=endFrame, step=self.stride.get(),
				recordArgs=recordArgs, encodeArgs=encodeArgs)

	Record = SaveModeless.Save

	def supersampleCB(self, *args):
		if self.supersample.get():
			self.samples.enable()
		else:
			self.samples.disable()
