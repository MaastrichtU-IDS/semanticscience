# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29790 2010-01-14 22:32:06Z pett $

def nw(s1, s2, scoreMatch=10, scoreMismatch=-3, scoreGap=0, scoreGapOpen=-40,
			gapChar=".", returnSeqs=False, scoreMatrix=None,
			similarityMatrix=None, frequencyMatrix=None,
			endsAreGaps=False, ssMatrix=None, ssFraction=0.9,
			gapOpenHelix=None, gapOpenStrand=None,
			gapOpenOther=None, debug=False):
	# if 'scoreMatrix', 'similarityMatrix', or 'frequencyMatrix' is
	# provided, then 'scoreMatch' and 'scoreMismatch' are ignored and
	# the matrix is used to evaluate matching between the sequences.
	# 'scoreMatrix' should be a two-dimensional array of size
	# len(s1) x len(s2).  'similarityMatrix' should be a dictionary
	# keyed with two-tuples of residue types.  'frequencyMatrix' should
	# be a list of length s2 of dictionaries, keyed by residue type.
	#
	# if 'ssFraction' is not None/False, then 'ssMatrix' should be a 3x3
	# matrix keyed with 2-tuples of secondary structure types ('H': helix,
	# 'S': strand, 'O': other).  The score will be a mixture of the
	# ss/similarity matrix scores weighted by the ssFraction
	# [ssFraction * ss score + (1 - ssFraction) * similarity score]
	#
	# if 'gapOpenHelix/Strand/Other' is not None and 'ssFraction' is not
	# None/False, then scoreGapOpen is ignored when an intra-helix/
	# intra-strand/other gap is opened and the appropriate penalty
	# is applied instead
	#
	# if 'returnSeqs' is True, then instead of returning a match list
	# (a list of two-tuples) as the second value, a two-tuple of gapped
	# Sequences will be returned.  In both cases, the first return value
	# is the match score.
	m = []
	bt = []
	for i1 in range(len(s1) + 1):
		m.append((len(s2) + 1) * [ 0 ])
		bt.append((len(s2) + 1) * [None])
		bt[i1][0] = 1
		if endsAreGaps and i1 > 0:
			m[i1][0] = scoreGapOpen + i1 * scoreGap
	for i2 in range(len(s2) + 1):
		bt[0][i2] = 2
		if endsAreGaps and i2 > 0:
			m[0][i2] = scoreGapOpen * i2 * scoreGap

	if similarityMatrix is not None:
		evaluate = lambda i1, i2: similarityMatrix[(s1[i1], s2[i2])]
	elif scoreMatrix is not None:
		evaluate = lambda i1, i2: scoreMatrix[i1][i2]
	elif frequencyMatrix is not None:
		evaluate = lambda i1, i2: frequencyMatrix[i2][s1[i1]]
	else:
		def evaluate(i1, i2):
			if s1[i1] == s2[i2]:
				return scoreMatch
			return scoreMismatch
	doingSS =  ssFraction is not None and ssFraction is not False \
						and ssMatrix is not None
	if doingSS:
		prevEval = evaluate
		simFraction = 1.0 - ssFraction
		def ssEval(i1, i2):
			if hasattr(s1, 'ssFreqs'):
				freqs1 = s1.ssFreqs[i1]
			else:
				freqs1 = {s1.ssType(i1): 1.0}
			if hasattr(s2, 'ssFreqs'):
				freqs2 = s2.ssFreqs[i2]
			else:
				freqs2 = {s2.ssType(i2): 1.0}
			val = 0.0
			for ss1, freq1 in freqs1.items():
				if ss1 == None:
					continue
				for ss2, freq2 in freqs2.items():
					if ss2 == None:
						continue
					val += freq1 * freq2 * ssMatrix[(ss1,
									ss2)]
			return val
		evaluate = lambda i1, i2: ssFraction * ssEval(i1, i2) + \
					simFraction * prevEval(i1, i2)

	# precompute appropriate gap-open penalties
	gapOpen1 = [scoreGapOpen] * (len(s1)+1)
	gapOpen2 = [scoreGapOpen] * (len(s2)+1)
	if endsAreGaps:
		if gapOpenOther is not None:
			gapOpen1[0] = gapOpen2[0] = gapOpenOther
	else:
			gapOpen1[0] = gapOpen2[0] = 0
	if doingSS and gapOpenOther != None:
		for seq, gapOpens in [(s1, gapOpen1), (s2, gapOpen2)]:
			if hasattr(seq, 'gapFreqs'):
				for i, gapFreq in enumerate(seq.gapFreqs):
					gapOpens[i+1] = \
						gapFreq['H'] * gapOpenHelix + \
						gapFreq['S'] * gapOpenStrand + \
						gapFreq['O'] * gapOpenOther
			else:
				ssTypes = [seq.ssType(i)
						for i in range(len(seq))]
				for i, ss in enumerate(ssTypes[:-1]):
					nextSS = ssTypes[i+1]
					if ss == nextSS and ss == 'H':
						gapOpens[i+1] = gapOpenHelix
					elif ss == nextSS and ss == 'S':
						gapOpens[i+1] = gapOpenStrand
					else:
						gapOpens[i+1] = gapOpenOther

	colGapStarts = [0] * len(s2) # don't care about column zero
	for i1 in range(len(s1)):
		rowGapPos = 0
		for i2 in range(len(s2)):
			best = m[i1][i2] + evaluate(i1, i2)
			btType = 0
			if i2 + 1 < len(s2) or endsAreGaps:
				colGapPos = colGapStarts[i2]
				skipSize = i1 + 1 - colGapPos
				if hasattr(s1, "occupancy"):
					totOcc = 0.0
					for i in range(colGapPos, i1+1):
						totOcc += s1.occupancy[i]
					colSkipVal = totOcc * scoreGap
				else:
					colSkipVal = skipSize * scoreGap
				baseColGapVal = m[colGapPos][i2+1] + colSkipVal
				skip = baseColGapVal + gapOpen2[i2+1]
			else:
				skipSize = 1
				colSkipVal = 0
				skip = m[i1][i2+1]
			if skip > best:
				best = skip
				btType = skipSize
			if i1 + 1 < len(s1) or endsAreGaps:
				skipSize = i2 + 1 - rowGapPos
				if hasattr(s2, "occupancy"):
					totOcc = 0.0
					for i in range(rowGapPos, i2+1):
						totOcc += s2.occupancy[i]
					rowSkipVal = totOcc * scoreGap
				else:
					rowSkipVal = skipSize * scoreGap
				baseRowGapVal = m[i1+1][rowGapPos] + rowSkipVal
				skip = baseRowGapVal + gapOpen1[i1+1]
			else:
				skipSize = 1
				rowSkipVal = 0
				skip = m[i1+1][i2]
			if skip > best:
				best = skip
				btType = 0 - skipSize
			m[i1+1][i2+1] = best
			bt[i1+1][i2+1] = btType
			if btType >= 0:
				# not gapping the row
				if best > baseRowGapVal:
					rowGapPos = i2 + 1
			if btType <= 0:
				# not gapping the column
				if best > baseColGapVal:
					colGapStarts[i2] = i1 + 1
	if debug:
		from chimera.selection import currentResidues
		cr = currentResidues(asDict=True)
		if cr:
			for fileName, matrix in [("scores", m), ("trace", bt)]:
				out = open("/home/socr/a/pett/rm/" + fileName,
									"w")
				print>>out, "    ",
				for i2, r2 in enumerate(s2.residues):
					if r2 not in cr:
						continue
					print>>out, "%5d" % i2,
				print>>out
				print>>out, "    ",
				for i2, r2 in enumerate(s2.residues):
					if r2 not in cr:
						continue
					print>>out, "%5s" % s2[i2],
				print>>out
				for i1, r1 in enumerate(s1.residues):
					if r1 not in cr:
						continue
					print>>out, "%3d" % i1, s1[i1],
					for i2, r2 in enumerate(s2.residues):
						if r2 not in cr:
							continue
						print>>out, "%5g" % (
							matrix[i1+1][i2+1]),
					print>>out
				out.close()
	i1 = len(s1)
	i2 = len(s2)
	matchList = []
	while i1 > 0 and i2 > 0:
		btType = bt[i1][i2]
		if btType == 0:
			matchList.append((i1-1, i2-1))
			i1 = i1 - 1
			i2 = i2 - 1
		elif btType > 0:
			i1 = i1 - btType
		else:
			i2 = i2 + btType
	if returnSeqs:
		return m[len(s1)][len(s2)], matches2gappedSeqs(matchList,
							s1, s2, gapChar=gapChar)
	return m[len(s1)][len(s2)], matchList

def matches2gappedSeqs(matches, s1, s2, gapChar=".", reverseSorts=True):
	gapped1 = cloneSeq(s1)
	gapped2 = cloneSeq(s2)
	prev1 = prev2 = -1
	if reverseSorts:
		matches.reverse()
	else:
		matches.sort()
	for pos1, pos2 in matches:
		if pos1 > prev1 + 1 and pos2 > prev2 + 1:
			gapped1.extend(s1[prev1+1:pos1])
			gapped2.extend(gapChar * (pos1 - prev1 - 1))
			gapped1.extend(gapChar * (pos2 - prev2 - 1))
			gapped1.append(s1[pos1])
			gapped2.extend(s2[prev2+1:pos2+1])
		else:
			if pos1 > prev1 + 1:
				gapped1.extend(s1[prev1+1:pos1+1])
				gapped2.extend(gapChar * (pos1 - prev1 - 1))
				gapped2.append(s2[pos2])
			if pos2 > prev2 + 1:
				gapped1.extend(gapChar * (pos2 - prev2 - 1))
				gapped1.append(s1[pos1])
				gapped2.extend(s2[prev2+1:pos2+1])
			if pos1 == prev1 + 1 and pos2 == prev2 + 1:
				gapped1.append(s1[pos1])
				gapped2.append(s2[pos2])
		prev1, prev2 = pos1, pos2
	if prev1 < len(s1) - 1:
		gapped2.extend(gapChar * (len(s1) - prev1 - 1))
		gapped1.extend(s1[prev1+1:])
	if prev2 < len(s2) - 1:
		gapped1.extend(gapChar * (len(s2) - prev2 - 1))
		gapped2.extend(s2[prev2+1:])
	return gapped1, gapped2

def cloneSeq(seq):
	from copy import copy
	clone = copy(seq)
	if hasattr(clone, "molecule"):
		name = clone.molecule.name
		if not clone.name.startswith("principal"):
			name += ", " + clone.name
		clone.name = name
	clone[:] = ""
	return clone

if __name__ == '__main__':
	print nw("abxxababxxab", "abab", endsAreGaps=True)
