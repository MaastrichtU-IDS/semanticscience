# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: structAssoc.py 29772 2010-01-13 22:25:03Z pett $

from chimera.Sequence import Sequence
from NeedlemanWunsch import nw

def tryAssoc(alignSeq, mseq, segments, gaps, estLen, maxErrors=6):
	aseq = alignSeq.ungapped().upper()

	valueError = False
	try:
		if len(aseq) >= estLen:
			matchMap, errors = constrainedMatch(aseq, mseq,
							segments, maxErrors)
		else:
			matchMap, errors = gappedMatch(aseq, mseq, segments,
							gaps, estLen, maxErrors)
	except ValueError:
		valueError = True

	# prune off 'X' residues and see how that works...
	if mseq[0] != 'X' and mseq[-1] != 'X':
		if valueError:
			raise ValueError, "bad assoc"
		return matchMap, errors
	from copy import copy
	noX = copy(mseq)
	while noX[:1] == 'X':
		noX.sequence = noX.sequence[1:]
		noX.residues = noX.residues[1:]
		estLen -= 1
	offset = len(mseq) - len(noX)
	Xsegments = copy(segments)
	if offset:
		Xsegments[0] = Xsegments[0][offset:]
	tailLoss = 0
	while noX[-1:] == 'X':
		noX.sequence = noX.sequence[:-1]
		noX.residues = noX.residues[:-1]
		estLen -= 1
		tailLoss += 1
	if tailLoss:
		Xsegments[-1] = Xsegments[-1][:-tailLoss]
	if len(noX) == 0:
		if valueError:
			raise ValueError, "bad assoc"
		return matchMap, errors
	try:
		if len(aseq) >= estLen:
			noXmatchMap, noXerrors = constrainedMatch(aseq, noX,
							Xsegments, maxErrors)
		else:
			noXmatchMap, noXerrors = gappedMatch(aseq, noX,
					Xsegments, gaps, estLen, maxErrors)
	except ValueError:
		if valueError:
			raise
		return matchMap, errors
	if valueError or noXerrors < errors:
		return noXmatchMap, noXerrors
	return matchMap, errors

def constrainedMatch(aseq, mseq, segments, maxErrors):
	# all the segments should fit in aseq

	offsets, errors = _constrained(aseq, segments, maxErrors)
	if errors > maxErrors:
		raise ValueError, "bad assoc"
	if len(offsets) != len(segments):
		raise AssertionError, \
			"Internal match problem: segments (%d) != offsets (%d)"\
			% (len(segments), len(offsets))
	matchMap = {}
	resOffset = 0
	for si in range(len(segments)):
		offset, segment = offsets[si], segments[si]
		for i in range(len(segment)):
			res = mseq.residues[resOffset+i]
			if res:
				matchMap[res] = offset+i
				matchMap[offset+i] = res
		resOffset += len(segment)
	return matchMap, errors

def _constrained(aseq, segments, maxErrors):
	# find the biggest segment
	longest = None
	for i in range(len(segments)):
		seg = segments[i]
		if not longest or len(seg) > longest:
			bsi = i
			longest = len(seg)
	from operator import add
	leftSpace = 0
	for seg in segments[:bsi]:
		leftSpace += 1 + len(seg)
	rightSpace = 0
	for seg in segments[bsi+1:]:
		rightSpace += 1 + len(seg)

	if len(aseq) - leftSpace - rightSpace < longest:
		return [], maxErrors + 1

	errList = []
	seq = segments[bsi]
	minOffset = None
	minErrs = None
	for offset in range(leftSpace, len(aseq) - rightSpace - longest + 1):
		errors = 0
		for i in range(longest):
			if seq[i] == aseq[offset+i]:
				continue
			errors += 1
			if errors > maxErrors:
				errList.append(maxErrors+1)
				break
		else:
			errList.append(errors)
			if minErrs is None or errors < minErrs:
				minErrs = errors
				minOffset = offset
	if minOffset is None:
		return [], maxErrors+1

	# leave gaps to left and right
	if bsi > 0:
		leftOffsets, leftErrors = _constrained(aseq[0:minOffset-1],
					segments[:bsi], maxErrors - minErrs)
	else:
		leftOffsets, leftErrors = [], 0

	if leftErrors + minErrs > maxErrors or bsi + 1 == len(segments):
		rightOffsets, rightErrors = [], 0
	else:
		rightOffsets, rightErrors = _constrained(
				aseq[minOffset+longest+1:], segments[bsi+1:],
				maxErrors - minErrs - leftErrors)
	totErrs = minErrs + leftErrors + rightErrors
	offs = (leftOffsets, minOffset, rightOffsets)

	for i in range(len(errList)):
		baseErrs = errList[i]
		if baseErrs >= min(totErrs, maxErrors+1):
			continue
		offset = leftSpace + i
		if offset == minOffset:
			continue

		if bsi > 0:
			leftOffsets, leftErrors = _constrained(aseq[0:offset-1],
					segments[:bsi],
					min(totErrs, maxErrors) - baseErrs)
		else:
			leftOffsets, leftErrors = [], 0
			
		if leftErrors + baseErrs > maxErrors:
			continue

		if bsi+1 < len(segments):
			rightOffsets, rightErrors = _constrained(
				aseq[offset+longest+1:], segments[bsi+1:],
				min(totErrs, maxErrors) - baseErrs - leftErrors)
		else:
			rightOffsets, rightErrors = [], 0

		if baseErrs + leftErrors + rightErrors < totErrs:
			totErrs = baseErrs + leftErrors + rightErrors
			offs = (leftOffsets, offset, rightOffsets)

	if totErrs > maxErrors:
		return [], maxErrors+1

	offsets = offs[0]
	offsets.append(offs[1])
	for ro in offs[2]:
		offsets.append(ro + offs[1] + longest + 1)

	return offsets, totErrs

def gappedMatch(aseq, mseq, segments, gaps, estLen, maxErrors):
	gapped = segments[0]
	for i in range(1, len(segments)):
		gapped += "." * gaps[i-1]
		gapped += segments[i]

	# to avoid matching completely in gaps, need to establish a 
	# minimum number of matches
	minMatches = min(len(aseq), len(mseq)) / 2
	bestScore = 0
	totErrs = maxErrors + 1
	for offset in range(len(gapped) - estLen, estLen - len(aseq) + 1):
		matches = 0
		errors = 0
		if offset + len(aseq) < minMatches:
			continue
		if len(gapped) - offset < minMatches:
			continue
		for i in range(len(aseq)):
			if offset + i < 0:
				continue
			try:
				gapChar = gapped[offset+i]
			except IndexError:
				# in ending gap
				continue
			if aseq[i] == gapChar:
				matches += 1
				continue
			if gapChar == ".":
				continue
			errors += 1
			if errors >= totErrs:
				break
		else:
			if matches < minMatches or matches-errors <= bestScore:
				continue
			bestScore = matches - errors
			totErrs = errors
			bestOffset = offset

	if totErrs > maxErrors:
		raise ValueError, "bad assoc"

	matchMap = {}
	mseqIndex = 0
	for i in range(bestOffset + len(aseq)):
		try:
			if gapped[i] == ".":
				continue
		except IndexError:
			# in ending gap
			break
		if i >= bestOffset:
			res = mseq.residues[mseqIndex]
			if res:
				aseqIndex = i - bestOffset
				matchMap[res] = aseqIndex
				matchMap[aseqIndex] = res
		mseqIndex += 1

	return matchMap, totErrs

def oldTryAssoc(alignSeq, molSeq, gappedMseq, maxErrors=6):
	# remove gaps in alignment sequence...
	mseq = molSeq
	aseq = alignSeq.ungapped().upper()

	if len(gappedMseq) > len(aseq):
		return dragMatch(aseq, gappedMseq, maxErrors)

	unmatched = [(len(mseq), ("initial", 0, len(aseq), 0, len(mseq)))]
	matchups = []
	forcedMatches = []
	sumMatched = 0
	forcedErrors = 0

	while len(unmatched) > 0:
		minErrors = len(matchups) - 1 + len(unmatched) + forcedErrors
		if minErrors > maxErrors:
			raise ValueError, "bad assoc"
		# the minimum number of identical matches required
		# for a matchup to possibly work out is...
		allowedErrors = maxErrors - minErrors + 1
		# round down since if number of allowed errors exceeds what
		# we still need to match, the minStretch is zero
		minStretch = int((len(mseq) - sumMatched - minErrors) /
							float(allowedErrors))
		side, aseqStart, aseqLength, mseqStart, mseqLength \
							= unmatched[0][1]
		unmatched = unmatched[1:]
		matchup = Matchup(aseq[aseqStart:aseqStart+aseqLength],
			mseq[mseqStart:mseqStart+mseqLength], minStretch)
		if matchup.best == None:
			if minStretch == 0 and side != "initial":
				fm, errs = makeForcedMatch(side, aseq, mseq,
							aseqStart, aseqLength,
							mseqStart, mseqLength)
				forcedMatches.append(fm)
				forcedErrors += errs
				if aseqLength == mseqLength \
				and mseqStart > 0 \
				and mseqStart + mseqLength < len(mseq):
					# if the forced errors fill an
					# internal gap, then reduce the
					# the errors by one to compensate
					# for the gap being gone
					forcedErrors -= 1
				continue
			raise ValueError, "bad assoc"
		matchup.aseqStart = aseqStart
		matchup.mseqStart = mseqStart
		matchups.append(matchup)
		offset, start, stretch = matchup.best
		sumMatched += stretch
		if start > 0:
			astart = aseqStart
			alen = offset + start
			mstart = mseqStart
			mlen = start
			if mlen == 1:
				forcedMatches.append((astart, mstart, 1))
				if alen > 1 or mstart == 0:
					# don't add an error if filling
					# an internal gap
					forcedErrors += 1
			else:
				unmatched.append((mlen,
					("left", astart, alen, mstart, mlen)))
		if start + stretch < mseqLength:
			astart = aseqStart + offset + start + stretch
			alen = aseqLength - offset - start - stretch
			mstart = mseqStart + start + stretch
			mlen = mseqLength - start - stretch
			if mlen == 1:
				forcedMatches.append((astart, mstart, 1))
				if alen > 1 or mstart + 1 == len(mseq):
					# don't add an error if filling
					# an internal gap
					forcedErrors += 1
			else:
				unmatched.append((mlen,
					("right", astart, alen, mstart, mlen)))
		unmatched.sort()
		unmatched.reverse()

	matchMap = {}
	for matchup in matchups:
		offset, start, stretch = matchup.best
		aStart = matchup.aseqStart + offset + start
		mStart = matchup.mseqStart + start
		for i in range(stretch):
			residue = mseq.residues[mStart + i]
			if residue:
				matchMap[aStart + i] = residue
				matchMap[residue] = aStart + i
	for aStart, mStart, stretch in forcedMatches:
		for i in range(stretch):
			residue = mseq.residues[mStart + i]
			if residue:
				matchMap[aStart + i] = residue
				matchMap[residue] = aStart + i
	return matchMap, len(matchups) - 1 + forcedErrors

def makeForcedMatch(side, aseq, mseq,
			aseqStart, aseqLength, mseqStart, mseqLength):
	if side == "left":
		astart = aseqStart
	else:
		astart = aseqStart + aseqLength - mseqLength
	errors = 0
	for i in range(mseqLength):
		if aseq[astart + i] != mseq[mseqStart + i]:
			errors += 1
	return ((astart, mseqStart, mseqLength), errors)

def dragMatch(aseq, gappedMseq, maxErrors):
	# mseq longer than aseq
	# can still be gaps in mseq

	# scan aseq along mseq looking for longest matching stretch...
	bestStretch = (None, None, 0, 0)
	for i in range(min(2 - len(aseq), 0), len(gappedMseq)):
		start = None
		if len(gappedMseq) - i <= bestStretch[-1]:
			break
		for j in range(min(len(aseq), len(gappedMseq)-i)):
			if i+j < 0:
				continue
			mval = gappedMseq[i+j]
			if mval == aseq[j] or mval == '-':
				if start is None:
					start = j
					matches = mval != '-'
				else:
					matches += mval != '-'
				if matches > bestStretch[-1]:
					bestStretch = (start, i+start,
							j - start + 1, matches)
			else:
				start = None
	a_off, m_off, length, matches = bestStretch
	if length < 2:
		if hasattr(gappedMseq, 'residues'):
			raise ValueError, "bad assoc"
		return []
	unmatched = len(aseq) - matches - aseq.count('-') 
	if unmatched / matches + 1 > maxErrors:
		raise ValueError, "bad assoc"
	matches = [[a_off, m_off, length]]
	furtherErrors = maxErrors - (m_off > 0) - (
					m_off + length < len(gappedMseq))
	if furtherErrors < 0:
		raise ValueError, "bad assoc"

	if a_off > 0 and m_off > 0:
		matches += dragMatch(aseq[:a_off], gappedMseq[:m_off],
								furtherErrors)

	if a_off + length < len(aseq) and m_off + length < len(gappedMseq):
		rMatches = dragMatch(aseq[a_off+length:],
				gappedMseq[m_off+length:], furtherErrors)
		for m in rMatches:
			m[0] += a_off + length
			m[1] += m_off + length
			matches.append(m)

	if not hasattr(gappedMseq, 'residues'):
		return matches

	matchMap = {}
	for m in matches:
		a_off, m_off, length = m
		for i in range(length):
			ungapped = gappedMseq.gapped2ungapped(m_off + i)
			if ungapped is None:
				continue
			res = gappedMseq.residues[ungapped]
			matchMap[res] = a_off + i
			matchMap[a_off + i] = res
	if not matchMap:
		raise ValueError, "bad assoc"

	# find gaps;
	# if mseq gap and aseq gap are same length: force match
	errors = left = gap = None
	for i in range(len(aseq)):
		if matchMap.has_key(i):
			last = i
			if errors is None:
				errors = i # e.g. 0 if first match at i == 0
			if gap is None:
				left = i
			else:
				# possible force
				mseqStart = gappedMseq.residues.index(
								matchMap[left])
				mseqEnd = gappedMseq.residues.index(matchMap[i])
				errors += max(mseqEnd - mseqStart - 1, 1)
				if errors > maxErrors:
					raise ValueError, "bad assoc"
				if mseqEnd - mseqStart != i - left:
					left = i
					gap = None
					continue
				for j in range(1, i - left):
					res = gappedMseq.residues[mseqStart + j]
					matchMap[res] = left + j
					matchMap[left + j] = res
				left = i
				gap = None
		else:
			if left is not None:
				gap = i
	errors += len(aseq) - last - 1
	if errors > maxErrors:
		raise ValueError, "bad assoc"
	return matchMap, errors

def nwAssoc(alignSeq, molSeq):
	mseq = molSeq
	aseq = alignSeq.ungapped()
	score, matchList = nw(mseq, aseq)

	errors = 0
	# matched are in reverse order...
	try:
		mEnd = matchList[0][0]
	except IndexError:
		mEnd = -1
	if mEnd < len(mseq) - 1:
		# trailing unmatched
		errors += len(mseq) - mEnd - 1

	matchMap = {}
	lastMatch = mEnd + 1
	for mIndex, aIndex in matchList:
		if mseq[mIndex] != aseq[aIndex]:
			errors += 1

		if mIndex < lastMatch - 1:
			# gap in structure sequence
			errors += lastMatch - mIndex - 1

		res = mseq.residues[mIndex]
		if res:
			matchMap[res] = aIndex
			matchMap[aIndex] = res

		lastMatch = mIndex
	if lastMatch > 0:
		# beginning unmatched
		errors += lastMatch

	if len(mseq) > len(aseq):
		# unmatched residues forced, reduce errors by that amount...
		errors -= len(mseq) - len(aseq)

	return matchMap, errors

class Matchup:
	""" When done, self.best will either be None or a 3-tuple.
	    If None, then no stretch of at least 'minStretch' matches
	    were found.
	    A 3-tuple indicates the best match match.  The components of
	    the 3-tuple are (offset, start, stretch):
	    
	       offset:  offset into 'aseq' for matchup of 'mseq'

	       start:  offset into 'mseq' where stretch of matches found

	       stretch:  length of consecutive matches found
	"""

	def __init__(self, aseq, mseq, minStretch):
		self.minStretch = minStretch
		self.best = None
		self.aseq = aseq
		self.mseq = mseq
		if self.minStretch > 1:
			self.stride = self.minStretch
		else:
			self.stride = 1
		for offset in range(len(aseq) - len(mseq) + 1):
			if self.stride > 1:
				self.strideLoop(offset)
			else:
				self.simpleLoop(offset)

	def simpleLoop(self, offset):
		mseq = self.mseq
		aseq = self.aseq
		curStretch = None
		best = None
		for i in range(len(mseq)):
			m = mseq[i]
			a = aseq[i + offset]
			if m == a:
				if curStretch:
					curStretch += 1
				else:
					curStretch = 1
					curStart = i
			else:
				if curStretch:
					if not best or curStretch > best[-1]:
						best = (curStart, curStretch)
					if best[-1] > 1:
						self.stride = best[-1]
						return self.strideLoop(offset,
							best=best,
							startIndex=i+1)
					curStretch = None
		if curStretch:
			if not best or curStretch > best[-1]:
				best = (curStart, curStretch)
		if best:
			if (self.best and best[-1] > self.best[-1]) \
			or (not self.best and best[-1] >= self.minStretch):
				start, stretch = best
				self.best = (offset, start, stretch)

	def strideLoop(self, offset, best=None, startIndex=0):
		mseq = self.mseq
		aseq = self.aseq
		for i in range(startIndex + self.stride - 1, len(mseq),
								self.stride):
			m = mseq[i]
			a = aseq[i + offset]
			if m == a:
				# go left to find start of stretch
				for left in range(i-1, -1, -1):
					if mseq[left] != aseq[left + offset]:
						start = left + 1
						break
				else:
					start = 0
				# go right to find end
				for right in range(i+1, len(mseq)):
					if mseq[right] != aseq[right + offset]:
						stretch = right - start
						break
				else:
					stretch = len(mseq) - start

				if not best or stretch > best[-1]:
					best = (start, stretch)
					if stretch > self.stride:
						self.stride = stretch
				return self.strideLoop(offset, best=best,
						startIndex=start+stretch+1)
		if best:
			if (self.best and best[-1] > self.best[-1]) \
			or (not self.best and best[-1] > self.minStretch):
				start, stretch = best
				self.best = (offset, start, stretch)

def estimateAssocParams(mseq):
	# find the apparent gaps in the structure, and estimate total length
	# of structure sequence given these gaps; make a list of the continuous
	# segments
	estLen, segments, gaps = _findGaps(mseq)
	for i in range(len(segments)):
		segments[i] = "".join(segments[i])

	# try to compensate for trailing/leading
	# gaps by looking at SEQRES records
	from chimera.Sequence import seqresSequences
	srSeqs = seqresSequences(mseq.molecule)
	if srSeqs is None:
		srSeqs = []
	matchingSR = None
	for sr in srSeqs:
		if sr.name == mseq.name:
			if matchingSR:
				matchingSR = None
				break
			matchingSR = sr
	if matchingSR and len(matchingSR) > estLen:
		estLen = len(matchingSR)
	return estLen, segments, gaps

def _findGaps(mseq):
	from chimera import bondsBetween
	prevRes = None
	estLen = 0
	segments = []
	gaps = []
	for i in range(len(mseq)):
		estLen += 1
		res = mseq.residues[i]
		if not res:
			# explicit gapping
			return len(mseq), [mseq[:]], []
		char = mseq[i]
		gap = 0
		if prevRes:
			connects = bondsBetween(prevRes, res, onlyOne=1)
			if not connects or connects[0].sqlength() > 9.0:
				gap = res.id.position - \
						prevRes.id.position - 1
				if gap < 1:
					# bad numbering; just jam the
					# sequence together and hope
					return len(mseq), [mseq[:]], []
				gaps.append(gap)
				estLen += gap
		if not prevRes or gap:
			curSeg = [char]
			segments.append(curSeg)
		else:
			curSeg.append(char)
		prevRes = res
	if estLen > 0 and mseq.residues[0].id.position > 1:
		estLen += mseq.residues[0].id.position - 1
	return estLen, segments, gaps
