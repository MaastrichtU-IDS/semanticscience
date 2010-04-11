# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Pmw
import Tkinter
try:
	import Midi
except ImportError:
	import FakeMidi
	Midi = FakeMidi

instruments = [
		 'None',
		 'AcousticBass',
		 'AcousticGrandPiano',
		 'AcousticGuitarNylon',
		 'AcousticGuitarSteel',
		 'AltoSax',
		 'BaritoneSax',
		 'Bassoon',
		 'BrassSection',
		 'BrightAcousticPiano',
		 'Celesta',
		 'Cello',
		 'ChurchOrgan',
		 'Clarinet',
		 'Clavi',
		 'Contrabass',
		 'Dulcimer',
		 'ElectricGrandPiano',
		 'ElectricGuitarClean',
		 'ElectricPiano1',
		 'ElectricPiano2',
		 'EnglishHorn',
		 'Flute',
		 'FrenchHorn',
		 'Glockenspiel',
		 'Harpsichord',
		 'Marimba',
		 'MusicBox',
		 'Oboe',
		 'Ocarina',
		 'OrchestralHarp',
		 'PanFlute',
		 'PercussiveOrgan',
		 'Piccolo',
		 'PizzicatoStrings',
		 'Recorder',
		 'ReedOrgan',
		 'RockOrgan',
		 'Shakuhachi',
		 'SopranoSax',
		 'StringEnsemble1',
		 'StringEnsemble2',
		 'SynthBass1',
		 'SynthBass2',
		 'SynthBrass1',
		 'SynthBrass2',
		 'SynthStrings1',
		 'SynthStrings2',
		 'TenorSax',
		 'Timpani',
		 'Trombone',
		 'Trumpet',
		 'Tuba',
		 'TubularBells',
		 'Vibraphone',
		 'Viola',
		 'Violin',
		 'Whistle',
		 'Xylophone',
]

instrumentMap = {}
instrNumberMap = {}
for instr in instruments:
	if instr == 'None':
		n = -1
	else:
		n = Midi.instrument(instr)
	instrumentMap[instr] = n
	instrNumberMap[n] = instr

class Sonify:

	def __init__(self, tk, midi):
		self.midi = midi
		self.top = self.makeUI(tk)
		self.top.withdraw()
		self.msgDialog = None
		self.fieldParams = {}
		self.channels = {}
		self.nextChannel = 0

	def makeUI(self, tk):
		root = Tkinter.Toplevel(tk)
		root.title('Sonification Parameters')
		root.protocol('WM_DELETE_WINDOW', self.hide)

		#
		# Instruments
		#
		g = Pmw.Group(root, tag_text='Instrument')
		g.grid(row=0, column=0, sticky='nsew')
		self.instrListbox = Pmw.ScrolledListBox(g.interior(),
					items=instruments,
					listbox_exportselection=Tkinter.FALSE,
					selectioncommand=self.enableButton)
		self.instrListbox.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)

		#
		# Pitch
		#
		g = Pmw.Group(root, tag_text='Pitch')
		g.grid(row=0, column=1, sticky='nsew')
		gi = g.interior()
		self.minPitch = Tkinter.Scale(gi,
					from_=127, to=0,
					orient=Tkinter.VERTICAL,
					command=self.enableButton)
		self.maxPitch = Tkinter.Scale(gi,
					from_=127, to=0,
					orient=Tkinter.VERTICAL,
					command=self.enableButton)
		l = Tkinter.Label(gi, text='Min', anchor=Tkinter.E)
		l.grid(row=0, column=0, sticky=Tkinter.E)
		self.minPitch.grid(row=1, column=0, sticky='ns')
		l = Tkinter.Label(gi, text='Max', anchor=Tkinter.E)
		l.grid(row=0, column=1, sticky=Tkinter.E)
		self.maxPitch.grid(row=1, column=1, sticky='ns')
		gi.rowconfigure(1, weight=1)

		#
		# Alarm parameters
		#
		self.alarmMode = Tkinter.IntVar(root)
		g = Pmw.Group(root,
				tag_pyclass=Tkinter.Checkbutton,
				tag_text='Sonify selected range only',
				tag_offvalue=0,
				tag_onvalue=1,
				tag_variable=self.alarmMode,
				tag_command=self.enableButton)
		g.grid(row=1, column=0, columnspan=2, sticky='nsew')
		gi = g.interior()
		l = Tkinter.Label(gi, text='Sonify only below this value:')
		l.grid(row=0, column=0)
		self.alarmLow = Tkinter.Entry(gi)
		self.alarmLow.grid(row=0, column=1)
		self.alarmLow.bind('<Key>', self.enableButton)
		l = Tkinter.Label(gi, text='Sonify only above this value:')
		l.grid(row=1, column=0)
		self.alarmHigh = Tkinter.Entry(gi)
		self.alarmHigh.grid(row=1, column=1) 
		self.alarmHigh.bind('<Key>', self.enableButton)
		gi.columnconfigure(1, weight=1)

		#
		# Set-values button
		#
		self.setButton = Tkinter.Button(root,
					text='Set Parameters' ,
					command=self.setValues)
		self.setButton.grid(row=2, column=0, columnspan=2,
					sticky=Tkinter.E)

		root.columnconfigure(0, weight=1)
		root.rowconfigure(0, weight=1)
		return root

	def enableButton(self, event=None):
		self.setButton['state'] = Tkinter.NORMAL

	def showMessage(self, msg):
		if self.msgDialog is None:
			self.msgDialog = Pmw.MessageDialog(
						title='Sonify Parameters')
		self.msgDialog.configure(message_text=msg)
		self.msgDialog.activate()
		
	def setValues(self):
		instrSel = self.instrListbox.curselection()[0]
		n = int(instrSel)
		instr = instrumentMap[instruments[n]]
		try:
			alarmLow = float(self.alarmLow.get())
		except ValueError:
			alarmLow = None
		try:
			alarmHigh = float(self.alarmHigh.get())
		except ValueError:
			alarmHigh = None
		try:
			channel = self.channels[self.currentField]
		except KeyError:
			channel = self.nextChannel
			self.nextChannel = self.nextChannel + 1
			self.channels[self.currentField] = channel
		if instr >= 0:
			self.midi.setInstrument(channel, instr)
		self.fieldParams[self.currentField] = [
			instr,
			channel,
			self.minPitch.get(),
			self.maxPitch.get(),
			self.alarmMode.get(),
			alarmLow,
			alarmHigh ]
		self.showMessage('Parameters set for field "%s"\n'
					'Instrument: %s\n'
					'Pitch: %d .. %d\n'
					'Alarm mode: %s\n'
					'Alarm below: %s\n'
					'Alarm above: %s'
					% (self.currentField,
					instruments[n],
					self.minPitch.get(),
					self.maxPitch.get(),
					self.alarmMode.get() and 'on' or 'off',
					str(alarmLow),
					str(alarmHigh)))
		self.setButton['state'] = Tkinter.DISABLED

	def parameters(self, field):
		if not self.fieldParams.has_key(field):
			return None
		values = self.fieldParams[field]
		if values[0] < 0:	# 'None' is -1
			return None
		return values

	def soundOptions(self, field):
		self.top.title('Sonification Parameters - %s' % field)
		self.currentField = field
		try:
			p = self.fieldParams[field]
			state = Tkinter.DISABLED
		except KeyError:
			p = (instrumentMap['SynthStrings1'], -1,
				40, 110, 0, None, None)
			state = Tkinter.NORMAL
		instr, ch, pMin, pMax, aMode, aLow, aHigh = p
		instrName = instrNumberMap[instr]
		n = instruments.index(instrName)
		listbox = self.instrListbox.component('listbox')
		listbox.select_clear(0, Tkinter.END)
		listbox.select_set(n)
		listbox.see(n)
		self.minPitch.set(pMin)
		self.maxPitch.set(pMax)
		self.alarmMode.set(aMode)
		self.alarmHigh.delete(0, Tkinter.END)
		if aHigh is not None:
			self.alarmHigh.insert(0, str(aHigh))
		self.alarmLow.delete(0, Tkinter.END)
		if aLow is not None:
			self.alarmLow.insert(0, str(aLow))
		self.top.deiconify()
		self.top.update_idletasks()
		self.setButton['state'] = state

	def hide(self):
		self.top.withdraw()

if __name__ == '__main__':
	midi = Midi.Output("Software Synth")
	s = Sonify(midi)
	app = Tkinter.Tk()
	top = Tkinter.Frame(app)
	top.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
	fields = [ 'van der Waals', 'Electrostatics', 'Total Energy' ]
	for f in fields:
		b = Tkinter.Button(top, text=f, command=lambda s=s, f=f:
							s.soundOptions(f))
		b.pack(side=Tkinter.TOP, fill=Tkinter.X)
	b = Tkinter.Button(top, text='Quit', command=app.quit)
	b.pack(side=Tkinter.TOP, fill=Tkinter.X)
	app.mainloop()
