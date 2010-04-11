from chimera import preferences

BOND_COLOR = 'bondColor'
RELAX_COLOR = 'relaxColor'
LINE_WIDTH = 'line width'

defaults = {
	BOND_COLOR: (0.0, 0.8, 0.9, 1.0),
	RELAX_COLOR: (0.95, 0.5, 0.0, 1.0),
	LINE_WIDTH: 1.0,
}
prefs = preferences.addCategory("FindHBonds", preferences.HiddenCategory,
						optDict=defaults.copy())
