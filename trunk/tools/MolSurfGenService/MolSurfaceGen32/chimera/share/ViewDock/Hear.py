# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Compound
try:
	import Midi
except ImportError:
	import FakeMidi
	Midi = FakeMidi

class HearResults(Compound.Results):

	def __init__(self, *args, **kw):
		Compound.Results.__init__(self, *args, **kw)

		#
		# calculate min and max values of fields
		#
		self.fieldLimits = {}
		for f in self.fields:
			minV = None
			maxV = None
			for c in self.compoundList:
				try:
					v = c.fields[f]
				except KeyError:
					continue
				if not isinstance(v, (int, float)):
					continue
				if minV is None or c.fields[f] < minV:
					minV = c.fields[f]
				if maxV is None or c.fields[f] > maxV:
					maxV = c.fields[f]
			if minV is not None \
			and maxV is not None \
			and minV < maxV:
				self.fieldLimits[f] = (minV, maxV)
		self.sonifyFields = self.fieldLimits.keys()

		#
		# check for external Midi Synth
		#
		try:
		       	self.midi = Midi.Output("Serial Port 2")
		except:
			self.midi = Midi.Output("Software Synth")
		#self.midi = Midi.Output("Software Synth")
		self.stopNotes = []

	def setSonify(self, sonify):
		self.sonify = sonify

	def movieStep(self, listbox):
		self._stopNotes()
		if not Compound.Results.movieStep(self, listbox):
			return None
		next = self.selected[0]
		for f in self.fields:
			p = self.sonify.parameters(f)
			if p is None:
				continue
			try:
				v = next.fields[f]
			except KeyError:
				continue
			instr, channel, minP, maxP, \
				alarmMode, minAlarm, maxAlarm = p
			minV, maxV = self.fieldLimits[f]
			if instr == None or maxV <= minV:
				continue
			if alarmMode == 0 \
			or (minAlarm is not None and v < minAlarm) \
			or (maxAlarm is not None and v > maxAlarm):
				range = float(maxV - minV)
				frac = (v - minV) / range
				note = int(frac * (maxP - minP) + minP)
				self.midi.noteOn(channel, note, 127)
				self.stopNotes.append((channel, note, 30))
		return 1

	def movieStop(self):
		Compound.Results.movieStop(self)
		self._stopNotes()

	def _stopNotes(self):
		if not self.stopNotes:
			return
		for args in self.stopNotes:
			apply(self.midi.noteOff, args)
		self.stopNotes = []
