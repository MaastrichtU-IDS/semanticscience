# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

self.schemas = ["Hydrophobic", "Positive", "Negative",
	"Polar", "Charged", "Small", "Tiny", "Aromatic", "Aliphatic"]
self.residues = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLU",
	"GLN", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE",
	"PRO", "SER", "THR", "TRP", "TYR", "VAL"]
self.selections = {
  "Hydrophobic": [1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1],
  "Positive": [0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  "Negative": [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  "Polar": [0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0],
  "Charged": [0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
  "Small": [1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],
  "Tiny": [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
  "Aromatic": [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0],
  "Aliphatic": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1] }

self.colorSchemes = {}
for schema in self.schemas:
	self.colorSchemes[schema] = {
		_strSelSide: 'green',
		_strUnselSide: 'yellow',
		_strSelMain: 'white',
		_strUnselMain: 'white',
		_strOther: None
	}
