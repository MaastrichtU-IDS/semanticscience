# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

instruments = [
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

class FakeMidi:
	def setInstrument(self, channel, instr):
		return

def Output(port):
	return FakeMidi()

def instrument(instr):
	try:
		return instruments.index(instr)
	except ValueError:
		return -1
