# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 29180 2009-10-29 00:13:47Z pett $

from chimera import preferences
from chimera.colorTable import colors
from MatchMaker.prefs import defaults as mmDefaults
from MatchMaker.prefs import USE_SS, SS_MIXTURE, SS_SCORES, HELIX_OPEN, \
	STRAND_OPEN, OTHER_OPEN, MATRIX, GAP_OPEN, GAP_EXTEND

SINGLE_PREFIX = "single-seq "
WRAP = "wrap"
WRAP_IF = "conditional wrap"
BLOCK_SPACE = "space between blocks"
LINE_WIDTH = "line width"
WRAP_THRESHOLD = "wrap threshold"
FONT_NAME = "font name"
FONT_SIZE = "font size"
BOLD_ALIGNMENT = "bold alignment"
COLUMN_SEP = "column separation (pixels)"
LINE_SEP = "line separation (pixels)"
TEN_RES_GAP = "space after 10 residues"
MATCH_CUTOFF = "match cutoff"
ASSESS_DIST = "assess match distance"
ASSESS_COLOR = "assess match region color"
LOAD_PDB_NAME_EXACT = "load PDB exact"
LOAD_PDB_NAME_START = "load PDB beginning"
LOAD_PDB_NAME_NCBI = "load PDB NCBI"
LOAD_PDB_NAME_VARSTART = "load PDB variable start"
LOAD_PDB_NAME_VARSTART_VAL = "load PDB variable start value"
LOAD_SCOP = "load SCOP"
LOAD_PDB_AUTO = "load PDB automatic"
LOAD_PDB_DO_LIMIT = "load PDB enforce limit"
LOAD_PDB_LIMIT = "load PDB limit"
ASSOC_ERROR_RATE = "maximum allowable struct assoc error rate"
CONSERVATION_STYLE = "conservation style"
CONSENSUS_STYLE = "consensus style"
RESIDUE_COLORING = "residue coloring"
SCF_COLOR_STRUCTURES = "scf colors structures"
SHOW_SEL = "show chimera selection"
NEW_REGION_BORDER = "new region border"
NEW_REGION_INTERIOR = "new region interior"
SEL_REGION_BORDER = "sel region border"
SEL_REGION_INTERIOR = "sel region interior"
SEQ_NAME_ELLIPSIS = "reduce seq name"
REGION_NAME_ELLIPSIS = "reduce region name"
MATCH_REG_ACTIVE = "draw match region"
MATCH_REG_EDGE = "match edge color"
MATCH_REG_FILL = "match fill color"
ERROR_REG_ACTIVE = "draw error region"
ERROR_REG_EDGE = "error edge color"
ERROR_REG_FILL = "error fill color"
GAP_REG_ACTIVE = "draw gap region"
GAP_REG_EDGE = "gap edge color"
GAP_REG_FILL = "gap fill color"
SHOW_CONSERVATION_AT_STARTUP = "startup conservation"
SHOW_CONSENSUS_AT_STARTUP = "startup consensus"
SHOW_RULER_AT_STARTUP = "startup ruler"

CSV_PERCENT = "identity histogram"
CSV_CLUSTAL_HIST = "Clustal histogram"
CSV_CLUSTAL_CHARS = "Clustal characters"
CSV_AL2CO = "AL2CO"
conservationStyles = [CSV_AL2CO, CSV_CLUSTAL_HIST, CSV_CLUSTAL_CHARS,
								CSV_PERCENT]

al2coFrequencies = ["unweighted", "modified Henikoff & Henikoff",
						"independent counts"]
AL2CO_FREQ = "al2co frequency"
al2coConservations = ["entropy-based", "variance-based", "sum of pairs"]
AL2CO_CONS = "al2co conservation"
AL2CO_WINDOW = "al2co window size"
AL2CO_GAP = "al2co gap fraction"
AL2CO_MATRIX = "al2co similarity matrix"
al2coTransforms = ["none", "normalization", "adjustment"]
AL2CO_TRANSFORM = "al2co matrix transformation"

CSN_MAJ_GAP = "majority in column including gaps"
CSN_MAJ_NOGAP = "majority in column ignoring gaps"
consensusStyles = [CSN_MAJ_GAP, CSN_MAJ_NOGAP]

RC_BLACK = "black"
RC_CLUSTALX = "Clustal X"
RC_HYDROPHOBICITY = "Kyte-Doolittle hydrophobicity"
RC_RIBBON = "ribbon"
RC_CUSTOM_SCHEMES = "custom residue-coloring schemes"
nonFileResidueColorings = [RC_BLACK, RC_CLUSTALX, RC_RIBBON]
builtinResidueColorings = nonFileResidueColorings + [RC_HYDROPHOBICITY]

defaults = {
	WRAP: False,
	WRAP_IF: True,
	LINE_WIDTH: 50,
	BLOCK_SPACE: True,
	SINGLE_PREFIX + WRAP: True,
	SINGLE_PREFIX + WRAP_IF: False,
	SINGLE_PREFIX + LINE_WIDTH: 50,
	SINGLE_PREFIX + BLOCK_SPACE: False,
	WRAP_THRESHOLD: 8,
	FONT_NAME: 'Helvetica',
	FONT_SIZE: 12,
	BOLD_ALIGNMENT: False,
	SINGLE_PREFIX + FONT_NAME: 'Helvetica',
	SINGLE_PREFIX + FONT_SIZE: 12,
	SINGLE_PREFIX + BOLD_ALIGNMENT: False,
	COLUMN_SEP: 0,
	LINE_SEP: 1,
	TEN_RES_GAP: True,
	SINGLE_PREFIX + COLUMN_SEP: -2,
	SINGLE_PREFIX + LINE_SEP: 8,
	SINGLE_PREFIX + TEN_RES_GAP: False,
	MATCH_CUTOFF: 2.0,
	ASSESS_DIST: 3.0,
	ASSESS_COLOR: map(lambda c: c/255.0, colors["dodger blue"]),
	LOAD_SCOP: 1,
	LOAD_PDB_NAME_EXACT: 1,
	LOAD_PDB_NAME_START: 1,
	LOAD_PDB_NAME_NCBI: 1,
	LOAD_PDB_NAME_VARSTART: 0,
	LOAD_PDB_NAME_VARSTART_VAL: "",
	LOAD_PDB_AUTO: 0,
	LOAD_PDB_DO_LIMIT: 1,
	LOAD_PDB_LIMIT: 10,
	ASSOC_ERROR_RATE: 10,
	CONSENSUS_STYLE: CSN_MAJ_GAP,
	CONSERVATION_STYLE: CSV_PERCENT,
	SHOW_CONSERVATION_AT_STARTUP: True,
	SHOW_CONSENSUS_AT_STARTUP: True,
	SHOW_RULER_AT_STARTUP: True,
	AL2CO_FREQ: 2,
	AL2CO_CONS: 0,
	AL2CO_WINDOW: 1,
	AL2CO_GAP: 0.5,
	AL2CO_MATRIX: "BLOSUM-62",
	AL2CO_TRANSFORM: 0,
	RESIDUE_COLORING: RC_CLUSTALX,
	SINGLE_PREFIX + RESIDUE_COLORING: RC_BLACK,
	RC_CUSTOM_SCHEMES: [],
	SCF_COLOR_STRUCTURES: 1,
	SHOW_SEL: 1,
	NEW_REGION_BORDER: None,
	NEW_REGION_INTERIOR: "white",
	SEL_REGION_BORDER: None,
	SEL_REGION_INTERIOR: "green",
	SEQ_NAME_ELLIPSIS: 30,
	REGION_NAME_ELLIPSIS: 25,
	MATRIX: mmDefaults[MATRIX],
	GAP_OPEN: mmDefaults[GAP_OPEN],
	GAP_EXTEND: mmDefaults[GAP_EXTEND],
	MATCH_REG_ACTIVE: False,
	MATCH_REG_EDGE: "black",
	MATCH_REG_FILL: None,
	ERROR_REG_ACTIVE: True,
	ERROR_REG_EDGE: None,
	ERROR_REG_FILL: "red",
	GAP_REG_ACTIVE: True,
	GAP_REG_EDGE: "red",
	GAP_REG_FILL: None,
	USE_SS: mmDefaults[USE_SS],
	SS_MIXTURE: mmDefaults[SS_MIXTURE],
	SS_SCORES: mmDefaults[SS_SCORES],
	HELIX_OPEN: mmDefaults[HELIX_OPEN],
	STRAND_OPEN: mmDefaults[STRAND_OPEN],
	OTHER_OPEN: mmDefaults[OTHER_OPEN],
}

from copy import deepcopy
prefs = preferences.addCategory("MultAlignViewer",
		preferences.HiddenCategory, optDict=deepcopy(defaults))
