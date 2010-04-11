# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29793 2010-01-15 00:48:19Z pett $

import SmithWaterman
import NeedlemanWunsch
from chimera.Sequence import StructureSequence
from chimera import replyobj, UserError, LimitationError

CP_SPECIFIC_SPECIFIC = "ss"
CP_SPECIFIC_BEST = "sb"
CP_BEST = "bb"

SA_NEEDLEMAN_WUNSCH = "Needleman-Wunsch"
SA_SMITH_WATERMAN = "Smith-Waterman"

from prefs import defaults, CHAIN_PAIRING, SEQUENCE_ALGORITHM, MATRIX, \
	GAP_OPEN, GAP_EXTEND, SS_MIXTURE, SS_SCORES, ITER_CUTOFF, HELIX_OPEN, \
	STRAND_OPEN, OTHER_OPEN, COMPUTE_SS
defaultSSMatrix = defaults[SS_SCORES]

def align(ref, match, matrix, algorithm, gapOpen, gapExtend, ksdsspCache,
					ssMatrix=defaults[SS_SCORES],
					ssFraction=defaults[SS_MIXTURE],
					gapOpenHelix=defaults[HELIX_OPEN],
					gapOpenStrand=defaults[STRAND_OPEN],
					gapOpenOther=defaults[OTHER_OPEN],
					computeSS=defaults[COMPUTE_SS]):
	similarityMatrix = SmithWaterman.matrices[matrix]
	ssf = ssFraction
	ssm = ssMatrix
	if ssf is not None and ssf is not False and computeSS:
		needCompute = []
		if ref.molecule not in ksdsspCache:
			needCompute.append(ref.molecule)
			ksdsspCache.add(ref.molecule)
		if match.molecule not in ksdsspCache:
			needCompute.append(match.molecule)
			ksdsspCache.add(match.molecule)
		if needCompute:
			from chimera.initprefs import ksdsspPrefs, \
					KSDSSP_ENERGY, KSDSSP_HELIX_LENGTH, \
					KSDSSP_STRAND_LENGTH
			from Midas import ksdssp
			ksdssp(needCompute, energy=ksdsspPrefs[KSDSSP_ENERGY],
				helixLen=ksdsspPrefs[KSDSSP_HELIX_LENGTH],
				strandLen=ksdsspPrefs[KSDSSP_STRAND_LENGTH])
	if algorithm == "nw":
		score, seqs = NeedlemanWunsch.nw(ref, match,
			scoreGap=-gapExtend, scoreGapOpen=0-gapOpen,
			similarityMatrix=similarityMatrix, returnSeqs=True,
			ssMatrix=ssMatrix, ssFraction=ssFraction,
			gapOpenHelix=-gapOpenHelix,
			gapOpenStrand=-gapOpenStrand,
			gapOpenOther=-gapOpenOther)
		gappedRef, gappedMatch = seqs
	elif algorithm =="sw":
		refName = ref.molecule.name
		if not ref.name.startswith("principal"):
			refName += ", " + ref.name
		gappedRef = StructureSequence(ref.molecule, refName)
		matchName = match.molecule.name
		if not match.name.startswith("principal"):
			matchName += ", " + match.name
		gappedMatch = StructureSequence(match.molecule, matchName)
		def ssLet(r):
			if not r:
				return ' '
			if r.isHelix:
				return 'H'
			elif r.isStrand:
				return 'S'
			return 'O'
		if ssf is False or ssf is None:
			ssf = 0.0
			ssm = None
		if ssm:
			# account for missing structure (blank SS letter)
			ssm = ssm.copy()
			for let in "HSO ":
				ssm[(let, ' ')] = 0.0
				ssm[(' ', let)] = 0.0
		score, alignment = SmithWaterman.align(str(ref), str(match),
			similarityMatrix, float(gapOpen), float(gapExtend),
			gapChar=".", ssMatrix=ssm, ssFraction=ssf,
			gapOpenHelix=float(gapOpenHelix),
			gapOpenStrand=float(gapOpenStrand),
			gapOpenOther=float(gapOpenOther),
			ss1="".join([ssLet(r) for r in ref.residues]),
			ss2="".join([ssLet(r) for r in match.residues]))
		gappedRef.extend(alignment[0])
		gappedMatch.extend(alignment[1])
		# Smith-Waterman may not be entirety of sequences...
		for orig, gapped in [(ref, gappedRef), (match, gappedMatch)]:
			ungapped = gapped.ungapped()
			for i in range(len(orig) - len(ungapped) + 1):
				if ungapped == orig[i:i+len(ungapped)]:
					break
			else:
				raise ValueError("Smith-Waterman result not"
					" a subsequence of original sequence")
			gapped.residues = orig.residues[i:i+len(ungapped)]
			resMap = {}
			gapped.resMap = resMap
			for j in range(len(ungapped)):
				resMap[gapped.residues[j]] = j
	else:
		raise ValueError("Unknown sequence alignment algorithm: %s"
								% algorithm)

	return score, gappedRef, gappedMatch

def matrixCompatible(chain, matrix):
	proteinMatrix = len(SmithWaterman.matrices[matrix]) >= 400
	return proteinMatrix == chain.hasProtein()

def match(chainPairing, matchItems, matrix, alg, gapOpen, gapExtend,
		iterate=None, showAlignment=False, align=align, **alignKw):
	"""Superimpose structures based on sequence alignment

	   'chainPairing' is the method of pairing chains to match:
	   
	   CP_SPECIFIC_SPECIFIC --
	   Each reference chain is paired with a specified match chain
	   
	   CP_SPECIFIC_BEST --
	   Single reference chain is paired with best seq-aligning
	   chain from one or more molecules

	   CP_BEST --
	   Best seq-aligning pair of chains from reference molecule and
	   match molecule(s) is used
	"""
	ksdsspCache = set()
	alg = alg.lower()
	if alg == "nw" or alg.startswith("needle"):
		alg = "nw"
		algName = "Needleman-Wunsch"
	elif alg =="sw" or alg.startswith("smith"):
		alg = "sw"
		algName = "Smith-Waterman"
	else:
		raise ValueError("Unknown sequence alignment algorithm: %s"
									% alg)
	pairings = {}
	smallMolErrMsg = "Reference and/or match model contains no nucleic or"\
		" amino acid chains.\nUse the command-line 'match' command" \
		" to superimpose small molecules/ligands."
	if chainPairing == CP_SPECIFIC_SPECIFIC:
		# specific chain(s) in each

		# various sanity checks
		#
		# (1) can't have same chain matched to multiple refs
		# (2) reference molecule can't be a match molecule
		matchChains = {}
		matchMols = {}
		refMols = {}
		for ref, match in matchItems:
			if not matrixCompatible(ref, matrix):
				raise UserError("Reference chain (%s) not"
					" compatible with %s similarity"
					" matrix" % (ref.fullName(), matrix))
			if not matrixCompatible(match, matrix):
				raise UserError("Match chain (%s) not"
					" compatible with %s similarity"
					" matrix" % (match.fullName(), matrix))
			if match in matchChains:
				raise UserError("Cannot match the same chain"
					" to multiple reference chains")
			matchChains[match] = ref
			if match.molecule in refMols \
			or ref.molecule in matchMols \
			or match.molecule == ref.molecule:
				raise UserError("Cannot have same molecule"
					" model provide both reference and"
					" match chains")
			matchMols[match.molecule] = ref
			refMols[ref.molecule] = match

		if not matchChains:
			raise UserError("Must select at least one reference"
								" chain.\n")

		for match, ref in matchChains.items():
			score, s1, s2 = align(ref, match, matrix, alg,
						gapOpen, gapExtend,
						ksdsspCache, **alignKw)
			pairings.setdefault(s2.molecule, []).append(
							(score, s1, s2))

	elif chainPairing == CP_SPECIFIC_BEST:
		# specific chain in reference;
		# best seq-aligning chain in match model(s)
		ref, matches = matchItems
		if not ref or not matches:
			raise UserError("Must select at least one reference"
							" and match item.\n")
		if not matrixCompatible(ref, matrix):
			raise UserError("Reference chain (%s) not compatible"
						" with %s similarity matrix"
						% (ref.fullName(), matrix))
		for match in matches:
			bestScore = None
			seqs = [s for s in match.sequences()
						if matrixCompatible(s, matrix)]
			if not seqs and match.sequences():
				raise UserError("No chains in match structure"
					" %s compatible with %s similarity"
					" matrix" % (match, matrix))
			for seq in seqs:
				score, s1, s2 = align(ref, seq, matrix, alg,
						gapOpen, gapExtend,
						ksdsspCache, **alignKw)
				if bestScore is None or score > bestScore:
					bestScore = score
					pairing = (score, s1, s2)
			if bestScore is None:
				raise LimitationError(smallMolErrMsg)
			pairings[match]= [pairing]

	elif chainPairing == CP_BEST:
		# best seq-aligning pair of chains between
		# reference and match structure(s)
		ref, matches = matchItems
		if not ref or not matches:
			raise UserError("Must select at least one reference"
				" and match item in different models.\n")
		rseqs = [s for s in ref.sequences()
					if matrixCompatible(s, matrix)]
		if not rseqs and ref.sequences():
			raise UserError("No chains in reference structure"
				" %s compatible with %s similarity"
				" matrix" % (ref, matrix))
		for match in matches:
			bestScore = None
			mseqs = [s for s in match.sequences()
						if matrixCompatible(s, matrix)]
			if not mseqs and match.sequences():
				raise UserError("No chains in match structure"
					" %s compatible with %s similarity"
					" matrix" % (match, matrix))
			for mseq in mseqs:
				for rseq in rseqs:
					score, s1, s2 = align(rseq, mseq,
						matrix, alg, gapOpen, gapExtend,
						ksdsspCache, **alignKw)
					if bestScore is None \
					or score > bestScore:
						bestScore = score
						pairing = (score,s1,s2)
			if bestScore is None:
				raise LimitationError(smallMolErrMsg)
			pairings[match]= [pairing]
	else:
		raise ValueError("No such chain-pairing method")

	from chimera.misc import principalAtom
	retVals = []
	for matchMol, pairs in pairings.items():
		refAtoms = []
		matchAtoms = []
		regionInfo = {}
		for score, s1, s2 in pairs:
			try:
				ssMatrix = alignKw['ssMatrix']
			except KeyError:
				ssMatrix = defaultSSMatrix
			try:
				ssFraction = alignKw['ssFraction']
			except KeyError:
				ssFraction = defaults[SS_MIXTURE]

			replyobj.status("match %s (%s) with %s (%s),"
				" score = %g\n" % (
				s1.name, s1.molecule.oslIdent(), s2.name,
				s2.molecule.oslIdent(), score), log=1)
			replyobj.info("with these parameters:\n"
				"\tchain pairing: %s\n\t%s using %s\n"
				% (chainPairing, algName, matrix))

			if ssFraction is None or ssFraction is False:
				replyobj.info("\tno secondary structure"
							" guidance used\n")
				replyobj.info("\tgap open %g, extend %g\n" % (
							gapOpen, gapExtend))
			else:
				if 'gapOpenHelix' in alignKw:
					gh = alignKw['gapOpenHelix']
				else:
					gh = defaults[HELIX_OPEN]
				if 'gapOpenStrand' in alignKw:
					gs = alignKw['gapOpenStrand']
				else:
					gs = defaults[STRAND_OPEN]
				if 'gapOpenOther' in alignKw:
					go = alignKw['gapOpenOther']
				else:
					go = defaults[OTHER_OPEN]
				replyobj.info("\tss fraction: %g\n"
					"\tgap open (HH/SS/other) %g/%g/%g, "
					"extend %g\n"
					"\tss matrix: " % (ssFraction, gh, gs,
					go, gapExtend))
				for ss1, ss2 in ssMatrix.keys():
					if ss2 < ss1:
						continue
					replyobj.info(" (%s, %s): %g" % (ss1,
						ss2, ssMatrix[(ss1, ss2)]))
				replyobj.info("\n")
			if iterate is None:
				replyobj.info("\tno iteration\n")
			else:
				replyobj.info("\titeration cutoff: %g\n"
								% iterate)
			if showAlignment:
				from MultAlignViewer.MAViewer import MAViewer
				mav = MAViewer([s1,s2], autoAssociate=None)
				mav.autoAssociate = True
				mav.hideHeaders(mav.headers(shownOnly=True))
				mav.showHeaders([h for h in mav.headers()
							if h.name == "RMSD"])
			for i in range(len(s1)):
				if s1[i] == "." or s2[i] == ".":
					continue
				refRes = s1.residues[s1.gapped2ungapped(i)]
				matchRes = s2.residues[s2.gapped2ungapped(i)]
				if not refRes:
					continue
				refAtom = principalAtom(refRes)
				if not refAtom:
					continue
				if not matchRes:
					continue
				matchAtom = principalAtom(matchRes)
				if not matchAtom:
					continue
				if refAtom.name != matchAtom.name:
					# nucleic P-only trace vs. full nucleic
					if refAtom.name != "P":
						try:
							refAtom = refAtom.residue.atomsMap["P"][0]
						except KeyError:
							continue
					else:
						try:
							matchAtom = matchAtom.residue.atomsMap["P"][0]
						except KeyError:
							continue
				refAtoms.append(refAtom)
				matchAtoms.append(matchAtom)
				if showAlignment and iterate is not None:
					regionInfo[refAtom] = (mav, i)
		import Midas
		if len(matchAtoms) < 3:
			replyobj.error("Fewer than 3 residues aligned; cannot"
				" match %s with %s\n" % (s1.name, s2.name))
			continue
		try:
			retVals.append(Midas.match(matchAtoms, refAtoms,
						iterate=iterate, minPoints=3))
		except Midas.TooFewAtomsError:
			replyobj.error("Iteration produces fewer than 3"
				" residues aligned.\nCannot match %s with %s"
				" satisfying iteration threshold.\n"
				% (s1.name, s2.name))
			continue
		replyobj.info("\n") # separate matches with whitespace
		if regionInfo:
			byMav = {}
			for ra in retVals[-1][1]:
				mav, index = regionInfo[ra]
				byMav.setdefault(mav, []).append(index)
			for mav, indices in byMav.items():
				indices.sort()
				from MultAlignViewer.MAViewer import \
							MATCHED_REGION_INFO
				name, fill, outline = MATCHED_REGION_INFO
				mav.newRegion(name=name, columns=indices,
						fill=fill, outline=outline)
				mav.status("Residues used in final fit"
						" iteration are highlighted")
	return retVals

def cmdMatch(refSel, matchSel, pairing=defaults[CHAIN_PAIRING],
		alg=defaults[SEQUENCE_ALGORITHM],
		ssFraction=defaults[SS_MIXTURE], matrix=defaults[MATRIX],
		gapOpen=defaults[GAP_OPEN], hgap=defaults[HELIX_OPEN],
		sgap=defaults[STRAND_OPEN], ogap=defaults[OTHER_OPEN],
		iterate=defaults[ITER_CUTOFF], gapExtend=defaults[GAP_EXTEND],
		showAlignment=False, computeSS=defaults[COMPUTE_SS],
		matHH=defaultSSMatrix[('H', 'H')],
		matSS=defaultSSMatrix[('S', 'S')],
		matOO=defaultSSMatrix[('O', 'O')],
		matHS=defaultSSMatrix[('H', 'S')],
		matHO=defaultSSMatrix[('H', 'O')],
		matSO=defaultSSMatrix[('S', 'O')]):
	"""wrapper for command-line command (friendlier args)"""
	from Midas import MidasError
	if matrix not in SmithWaterman.matrices:
		raise MidasError("No such matrix name: %s" % str(matrix))
	try:
		gapOpen + 1
		gapExtend + 1
		hgap + 1
		sgap + 1
		ogap + 1
	except TypeError:
		raise MidasError("Gap open/extend penalties must be numeric")
	if pairing == CP_SPECIFIC_SPECIFIC:
		matches = matchSel.chains()
	elif pairing == CP_SPECIFIC_BEST:
		matches = matchSel.molecules()
	if pairing == CP_SPECIFIC_SPECIFIC or pairing == CP_SPECIFIC_BEST:
		refs = refSel.chains()
		if not refs:
			raise MidasError("No reference chains specified")
		if pairing == CP_SPECIFIC_BEST and len(refs) > 1:
			raise MidasError("Specify a single reference"
								" chain only")
	else:
		refMols = refSel.molecules()
		if not refMols:
			raise MidasError("No reference model specified")
		if len(refMols) > 1:
			raise MidasError("Specify a single reference"
								" model only")
		refs = refMols
		matches = matchSel.molecules()
	if not matches:
		raise MidasError("No molecules/chains to match specified")
	for ref in refs:
		if ref in matches:
			matches.remove(ref)
	if not matches:
		raise MidasError("Must use different reference and match"
								" structures")
	if pairing == CP_SPECIFIC_SPECIFIC:
		if len(refs) != len(matches):
			raise MidasError("Different number of reference/match"
					" chains (%d ref, %d match)" %
					(len(refs), len(matches)))
		matchItems = zip(refs, matches)
	else:
		matchItems = (refs[0], matches)
	ssMatrix = {}
	ssMatrix[('H', 'H')] = float(matHH)
	ssMatrix[('S', 'S')] = float(matSS)
	ssMatrix[('O', 'O')] = float(matOO)
	ssMatrix[('H', 'S')] = ssMatrix[('S', 'H')] = float(matHS)
	ssMatrix[('H', 'O')] = ssMatrix[('O', 'H')] = float(matHO)
	ssMatrix[('S', 'O')] = ssMatrix[('O', 'S')] = float(matSO)
	if type(iterate) == bool and not iterate:
		iterate = None
	try:
		match(pairing, matchItems, matrix, alg, gapOpen, gapExtend,
			ssFraction=ssFraction, ssMatrix=ssMatrix,
			iterate=iterate, showAlignment=showAlignment,
			gapOpenHelix=hgap, gapOpenStrand=sgap,
			gapOpenOther=ogap, computeSS=computeSS)
	except UserError, v:
		raise MidasError, v
