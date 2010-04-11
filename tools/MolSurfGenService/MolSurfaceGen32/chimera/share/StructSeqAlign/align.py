# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: align.py 26938 2009-02-19 00:56:02Z pett $

from chimera import replyobj

def match2align(chains, cutoff, matchType, gapChar, circular, statusPrefix=""):
	if len(chains) == 2 and not circular:
		scores, seqs = pairAlign(chains, cutoff, gapChar,
			statusPrefix=statusPrefix)
	else:
		seqs = multiAlign(chains, cutoff, matchType, gapChar, circular,
			statusPrefix=statusPrefix)
	return seqs

def pairAlign(chains, cutoff, gapChar, statusPrefix=""):
	chain1, chain2 = chains

	# go through chain 1 and put each residue's principal
	# atom in a spatial tree
	from chimera.misc import principalAtom
	from CGLutil.AdaptiveTree import AdaptiveTree
	xyzs = []
	data = []
	for i in range(len(chain1)):
		res = chain1.residues[i]
		pa = principalAtom(res)
		if not pa:
			replyobj.warning("Cannot determine principal"
					" atom for residue %s\n"
					% res.oslIdent())
			continue
		xyzs.append(pa.xformCoord().data())
		data.append((i, pa.xformCoord()))
	tree = AdaptiveTree(xyzs, data, cutoff)

	# initialize score array
	from numpy import zeros
	scores = zeros((len(chain1),len(chain2)), float)
	scores -= 1.0

	# find matches and update score array
	for i2 in range(len(chain2)):
		res = chain2.residues[i2]
		pa = principalAtom(res)
		if not pa:
			replyobj.warning("Cannot determine principal"
					" atom for residue %s\n"
					% res.oslIdent())
			continue
		coord2 = pa.xformCoord()
		matches = tree.searchTree(coord2.data(), cutoff)
		for i1, coord1 in matches:
			dist = coord1.distance(coord2)
			if dist > cutoff:
				continue
			scores[i1][i2] = cutoff - dist

	# use NeedlemanWunsch to establish alignment
	from NeedlemanWunsch import nw
	score, seqs = nw(chain1, chain2, scoreMatrix=scores, gapChar=gapChar,
			returnSeqs=True, scoreGap=0, scoreGapOpen=0)
	smallest = min(len(chain1), len(chain2))
	minDots = max(len(chain1), len(chain2)) - smallest
	extraDots = len(seqs[0]) - smallest - minDots
	numMatches = smallest - extraDots
	replyobj.status("%s%d residue pairs aligned\n"
				% (statusPrefix, numMatches), log=True)

	if numMatches == 0:
		from chimera import UserError
		raise UserError("Cannot generate alignment because no"
					" residues within cutoff distance")
		
	return score, seqs

def multiAlign(chains, cutoff, matchType, gapChar, circular, statusPrefix=""):
	# create list of pairings between sequences
	# and prune to be monotonic
	trees = {}

	if matchType == "all":
		valFunc = min
	else:
		valFunc = max

	# for each pair, go through the second chain residue by residue
	# and compile crosslinks to other chain.  As links are compiled,
	# figure out what previous links are crossed and keep a running 
	# "penalty" function for links based on what they cross.
	# Sort links by penalty and keep pruning worst link until no links
	# cross.
	from chimera.misc import principalAtom
	from CGLutil.AdaptiveTree import AdaptiveTree

	class EndPoint:
		def __init__(self, seq, pos):
			self.seq = seq
			self.pos = pos

		def contains(self, seq, pos):
			return seq == self.seq and pos == self.pos

		def __getattr__(self, attr):
			if attr == "positions":
				return { self.seq: self.pos }
			raise AttributeError, \
				"No such EndPoint attribute: %s" % attr
		def __str__(self):
			from chimera import SelResidue
			if circular and self.pos >= len(self.seq):
				insert = " (circular 2nd half)"
				pos = self.pos - len(self.seq)
			else:
				pos = self.pos
				insert = ""
			return "EndPoint[(%s %s, %s%s)]" % (self.seq.molecule.name, self.seq.name, self.seq.residues[pos].oslIdent(SelResidue), insert)

	class Link:
		def __init__(self, info1, info2, val, doPenalty=False):
			self.info = [info1, info2]
			self.val = val
			if doPenalty:
				self.penalty = 0
				self.crosslinks = []

		def contains(self, seq, pos):
			return self.info[0].contains(seq, pos) \
				or self.info[1].contains(seq. pos)

		def evaluate(self):
			self.val = None
			for s1, p1 in self.info[0].positions.items():
				if circular and s1.circular and p1 >= len(s1):
					p1 -= len(s1)
				pa1 = pas[s1][p1]
				for s2, p2 in self.info[1].positions.items():
					if circular and s2.circular \
					and p2 >= len(s2):
						p2 -= len(s2)
					pa2 = pas[s2][p2]
					val = cutoff - pa1.xformCoord(
						).distance(pa2.xformCoord())
					if self.val is None:
						self.val = val
						continue
					self.val = valFunc(self.val, val)
					if valFunc == min and self.val < 0:
						break
				if valFunc == min and self.val < 0:
					break

		def __str__(self):
			return "Link(%s, %s)" % tuple(map(str, self.info))

	allLinks = []
			
	pas = {}
	pairings = {}
	replyobj.status("%sFinding residue principal atoms\n" % statusPrefix,
							blankAfter=0)
	for seq in chains:
		seqpas = []
		pairing = []
		for res in seq.residues:
			pa = principalAtom(res)
			pairing.append([])
			if circular:
				pairing.append([])
			if not pa:
				replyobj.warning("Cannot determine principal "
				  "atom for residue %s\n" % res.oslIdent())
				seqpas.append(None)
				continue
			seqpas.append(pa)
		pas[seq] = seqpas
		pairings[seq] = pairing
				

	if circular:
		circularPairs = {}
		holdData = {}
	tagTmpl = "(%%d/%d)" % ((len(chains)) * (len(chains)-1) / 2)
	num = 0
	for i, seq1 in enumerate(chains):
		len1 = len(pairings[seq1])
		for seq2 in chains[i+1:]:
			num += 1
			tag = tagTmpl % num
			len2 = len(pairings[seq2])
			links1 = []
			for i in range(len1):
				links1.append([])
			links2 = []
			for i in range(len2):
				links2.append([])
			linkList = []
			replyobj.status("%sBuilding search tree %s\n"
					% (statusPrefix, tag), blankAfter=0)
			try:
				tree = trees[seq2]
			except KeyError:
				xyzs = []
				data = []
				for i, pa in enumerate(pas[seq2]):
					if pa is None:
						continue
					xyzs.append(pa.xformCoord().data())
					data.append((i, pa))
				tree = AdaptiveTree(xyzs, data, cutoff)
			replyobj.status("%sSearching tree, building links %s\n"
					% (statusPrefix, tag), blankAfter=0)
			for i1, pa1 in enumerate(pas[seq1]):
				if pa1 is None:
					continue
				crd1 = pa1.xformCoord()
				matches = tree.searchTree(crd1.data(), cutoff)
				for i2, pa2 in matches:
					dist = crd1.distance(pa2.xformCoord())
					val = cutoff - dist
					if val <= 0:
						continue
					link = Link(EndPoint(seq1, i1),
						EndPoint(seq2, i2), val,
						doPenalty=True)
					links1[i1].append(link)
					links2[i2].append(link)
					linkList.append(link)

			if circular:
				replyobj.status("%sDetermining circularity %s\n"
					% (statusPrefix, tag), blankAfter=0)
				holdData[(seq1, seq2)] = (links1, links2,
								linkList)
				if len(linkList) < 2:
					replyobj.info("Less than 2 close"
						" residues for %s and %s\n"
						% (seq1.molecule.name,
						seq2.molecule.name))
					continue
				# determine optimal permutation of 1st seq;
				#
				# for each pair of links, find the permutation
				# where they begin to cross/uncross.  Use an
				# array to tabulate number of crossings for
				# each permutation.
				crossings = [0] * len(seq1)
				c2 = [0] * len(seq2)
				from random import sample
				numSamples = 5 * (len(seq1)+len(seq2))
				for ignore in range(numSamples):
					link1, link2 = sample(linkList, 2)
					l1p1 = link1.info[0].pos
					l1p2 = link1.info[1].pos
					l2p1 = link2.info[0].pos
					l2p2 = link2.info[1].pos
					if l1p1 == l2p1 \
					or l1p2 == l2p2:
						# can never cross
						continue
					first = len(seq1) - max(l1p1,
								l2p1)
					second = len(seq1) - min(l1p1,
								l2p1)
					if (l1p1 < l2p1) == (
							l1p2 < l2p2):
						# not crossed initially;
						# will cross when first
						# one permutes off end
						# and uncross when 2nd
						# one permutes off
						ranges = [(first,
							second)]
					else:
						# crossed initially
						ranges = [(0, first)]
						if second < len(seq1):
							ranges.append(
							(second,
							len(seq1)))
					for start, stop in ranges:
						for i in range(start,
								stop):
							crossings[i] +=1
					first = len(seq2) - max(l1p2,
								l2p2)
					second = len(seq2) - min(l1p2,
								l2p2)
					if (l1p1 < l2p1) == (
							l1p2 < l2p2):
						# not crossed initially;
						# will cross when first
						# one permutes off end
						# and uncross when 2nd
						# one permutes off
						ranges = [(first,
							second)]
					else:
						# crossed initially
						ranges = [(0, first)]
						if second < len(seq2):
							ranges.append(
							(second,
							len(seq2)))
					for start, stop in ranges:
						for i in range(start,
								stop):
							c2[i] +=1
				# to avoid dangling ends causing bogus
				# "circularities", the zero permutation has
				# to be beaten significantly for a 
				# circularity to be declared
				least = crossings[0] - 5*numSamples / len(seq1)
				permute1 = [0]
				for i, crossed in enumerate(crossings):
					if crossed < least:
						least = crossed
						permute1 = [i]
					elif crossed == least:
						permute1.append(i)
				least = c2[0] - 5*numSamples / len(seq2)
				permute2 = [0]
				for i, crossed in enumerate(c2):
					if crossed < least:
						least = crossed
						permute2 = [i]
					elif crossed == least:
						permute2.append(i)
				if permute1[0] != 0 and permute2[0] != 0:
					circularPairs[(seq1, seq2)] = (
						permute1[0], permute2[0])
					replyobj.info("%s %s / %s %s: permute %s by %d or %s by %d\n" % (seq1.molecule.name, seq1.name, seq2.molecule.name, seq2.name, seq1.molecule.name, permute1[0], seq2.molecule.name, permute2[0]))
				
			else:
				findPruneCrosslinks(allLinks, pairings, seq1,
					seq2, linkList, links1, links2, tag=tag,
					statusPrefix=statusPrefix)

	if circular:
		replyobj.status("%sMinimizing circularities\n" % statusPrefix,
							blankAfter=0)
		circulars = {}
		while 1:
			circularVotes = {}
			for seq1, seq2 in circularPairs.keys():
				if seq1 in circulars or seq2 in circulars:
					continue
				circularVotes[seq1] = circularVotes.get(seq1,
									0) + 1
				circularVotes[seq2] = circularVotes.get(seq2,
									0) + 1
			if not circularVotes:
				break
			candidates = circularVotes.keys()
			candidates.sort(lambda c1, c2: cmp(circularVotes[c2],
							circularVotes[c1]))
			circulars[candidates[0]] = True

		# has to be circular against every non-circular sequence
		# (avoid spurious circularities)
		ejected = True
		while ejected:
			ejected = False
			for cseq in circulars:
				for seq in chains:
					if seq in circulars:
						continue
					if (cseq, seq) not in circularPairs \
					and (seq, cseq) not in circularPairs:
						del circulars[cseq]
						ejected = True
						break
				if ejected:
					break

		for seq in chains:
			seq.circular = seq in circulars
			if seq.circular:
				replyobj.info("circular: %s\n"
							% seq.molecule.name)
		replyobj.status("%sAdjusting links for circular sequences\n"
						% statusPrefix, blankAfter=0)
		for seq1, seq2 in holdData.keys():
			if not seq1.circular and not seq2.circular:
				continue
			links1, links2, linkList = holdData[(seq1, seq2)]
			use1 = seq1.circular
			if seq1.circular and seq2.circular:
				if (seq1, seq2) in circularPairs:
					permute1, permute2 = circularPairs[
								(seq1, seq2)]
				elif (seq2, seq1) in circularPairs:
					permute2, permute1 in circularPairs[
								(seq2, seq1)]
				else:
					continue
				use1 =  len(seq1) - permute1 \
							< len(seq2) - permute2
			if use1:
				adjust, other = seq1, seq2
				links = links1
			else:
				adjust, other = seq2, seq1
				links = links2
			if (adjust, other) in circularPairs:
				permute = circularPairs[(adjust, other)][0]
			elif (other, adjust) in circularPairs:
				permute = circularPairs[(other, adjust)][1]
			else:
				continue
			fixup = len(adjust) - permute
			for link in linkList[:]: # append happens in loop
				if link.info[0].seq == adjust:
					myEnd = link.info[0]
					otherEnd = link.info[1]
				else:
					myEnd = link.info[1]
					otherEnd = link.info[0]
				if myEnd.pos >= fixup:
					continue
				links[myEnd.pos].remove(link)
				myEnd.pos += len(adjust)
				links[myEnd.pos].append(link)

		for i, seqs in enumerate(holdData.keys()):
			seq1, seq2 = seqs
			links1, links2, linkList = holdData[seqs]
			findPruneCrosslinks(allLinks, pairings, seq1, seq2,
				linkList, links1, links2, tag=tagTmpl % (i+1),
				statusPrefix=statusPrefix)
				
	class Column:
		def __init__(self, positions):
			if isinstance(positions, Column):
				self.positions = positions.positions.copy()
			else:
				self.positions = positions

		def contains(self, seq, pos):
			return seq in self.positions \
				and self.positions[seq] == pos

		def participation(self):
			p = 0
			members = self.positions.items()
			for i, sp in enumerate(members):
				seq1, pos1 = sp
				if circular and seq1.circular \
				and pos1 >= len(seq1):
					pos1 -= len(seq1)
				pa1 = pas[seq1][pos1]
				for seq2, pos2 in members[i+1:]:
					if circular and seq2.circular \
					and pos2 >= len(seq2):
						pos2 -= len(seq2)
					pa2 = pas[seq2][pos2]
					val = cutoff - pa1.xformCoord(
						).distance(pa2.xformCoord())
					p += val
			return p

		def value(self):
			value = None
			info = self.positions.items()
			for i, sp in enumerate(info):
				seq1, pos1 = sp
				if circular and seq1.circular \
				and pos1 >= len(seq1):
					pos1 -= len(seq1)
				pa1 = pas[seq1][pos1]
				for seq2, pos2 in info[i+1:]:
					if circular and seq2.circular \
					and pos2 >= len(seq2):
						pos2 -= len(seq2)
					pa2 = pas[seq2][pos2]
					val = cutoff - pa1.xformCoord(
						).distance(pa2.xformCoord())
					if value is None:
						value = val
						continue
					value = valFunc(value, val)
					if valFunc == min and value < 0:
						break
				if valFunc == min and value < 0:
					break
			return value

		def __str__(self):
			from chimera import SelResidue
			def circComp(seq, pos):
				if circular and seq.circular and pos>=len(seq):
					return pos - len(seq)
				return pos
			return "Column[" + ",".join(map(lambda i: "(%s %s, %s)" % (i[0].molecule.name, i[0].name, i[0].residues[circComp(i[0],i[1])].oslIdent(SelResidue)), self.positions.items())) + "]"
				
	columns = {}
	partialOrder = {}
	for seq in chains:
		columns[seq] = {}
		partialOrder[seq] = []

	seen = {}
	while allLinks:
		replyobj.status("%sForming columns (%d links to check)\n"
						% (statusPrefix, len(allLinks)))
		if allLinks[-1].val != max(map(lambda l: l.val, allLinks)):
			allLinks.sort(lambda l1, l2: cmp(l1.val, l2.val))
			if valFunc == min:
				while len(allLinks) > 1 \
				and allLinks[0].val <= 0:
					allLinks.pop(0)

		link = allLinks.pop()
		if link.val < 0:
			break
		key = tuple(link.info)
		if key in seen:
			continue
		seen[key] = 1
		for info in link.info:
			for seq, pos in info.positions.items():
				pairings[seq][pos].remove(link)

		checkInfo = {}
		checkInfo.update(link.info[0].positions)
		checkInfo.update(link.info[1].positions)
		okay = True
		for seq in link.info[0].positions.keys():
			if seq in link.info[1].positions:
				okay = False
				break
		if not okay or not _check(checkInfo, partialOrder, chains):
			continue

		col = Column(checkInfo)
		for seq, pos in checkInfo.items():
			po = partialOrder[seq]
			for i, pcol in enumerate(po):
				if pcol.positions[seq] > pos:
					break
			else:
				i = len(po)
			po.insert(i, col)
			cols = columns[seq]
			cols[col] = i
			for ncol in po[i+1:]:
				cols[ncol] += 1
		for info in link.info:
			for seq, pos in info.positions.items():
				for l in pairings[seq][pos]:
					if l.info[0].contains(seq, pos):
						base, connect = l.info
					else:
						connect, base = l.info
					l.info = [col, connect]
					l.evaluate()
					for cseq, cpos in col.positions.items():
						if base.contains(cseq, cpos):
							continue
						pairings[cseq][cpos].append(l)
			if isinstance(info, Column):
				for seq in info.positions.keys():
					seqCols = columns[seq]
					opos = seqCols[info]
					po = partialOrder[seq]
					partialOrder[seq] = po[:opos] \
								+ po[opos+1:]
					for pcol in partialOrder[seq][opos:]:
						seqCols[pcol] -= 1
					del seqCols[info]

	replyobj.status("%s Collating columns\n" % statusPrefix, blankAfter=0)

	orderedColumns = []
	while 1:
		# find an initial sequence column that can lead
		for seq in partialOrder.keys():
			try:
				col = partialOrder[seq][0]
			except IndexError:
				from chimera import UserError
				raise UserError("Cannot generate alignment with"
					" %s %s because it is not superimposed"
					" on the other structures" %
					(seq.molecule.name, seq.name))
			for cseq in col.positions.keys():
				if partialOrder[cseq][0] != col:
					break
			else:
				# is initial element for all sequences involved
				break
		else:
			break

		orderedColumns.append(col)
		for cseq in col.positions.keys():
			partialOrder[cseq].pop(0)
			if not partialOrder[cseq]:
				del partialOrder[cseq]
		# try to continue using this sequence as long as possible
		while seq in partialOrder:
			col = partialOrder[seq][0]
			for cseq in col.positions.keys():
				if partialOrder[cseq][0] != col:
					break
			else:
				orderedColumns.append(col)
				for cseq in col.positions.keys():
					partialOrder[cseq].pop(0)
					if not partialOrder[cseq]:
						del partialOrder[cseq]
				continue
			break

	from NeedlemanWunsch import cloneSeq
	clone = {}
	current = {}
	for seq in chains:
		clone[seq] = cloneSeq(seq)
		current[seq] = -1
		if circular:
			clone[seq].circular = seq.circular
			if seq.circular:
				clone[seq].name = "2 x " + clone[seq].name

	if not orderedColumns:
		replyobj.status("")
		replyobj.error("No residues satisfy distance constraint"
							" for column!\n")
		return

	# for maximum benefit from the "column squeezing" step that follows,
	# we need to add in the one-residue columns whose position is
	# well-determined
	newOrdered = [orderedColumns[0]]
	for col in orderedColumns[1:]:
		gap = None
		for seq, pos in newOrdered[-1].positions.items():
			if seq not in col.positions:
				continue
			if col.positions[seq] == pos + 1:
				continue
			if gap is not None:
				# not well-determined
				gap = None
				break
			gap = seq
		if gap is not None:
			for pos in range(newOrdered[-1].positions[gap]+1, 
							col.positions[gap]):
				newOrdered.append(Column({gap: pos}))
		newOrdered.append(col)
	orderedColumns = newOrdered

	# Squeeze column where possible:
	#
	# 	Find pairs of columns where the left-hand one could accept
	#	one or more residues from the right-hand one
	#
	#	Keep looking right (if necessary) to until each row has at
	#	least one gap, but no more than one
	#
	#	Squeeze
	colIndex = 0
	while colIndex < len(orderedColumns) - 1:
		replyobj.status("%sMerging columns (%d/%d)\n" % (statusPrefix,
				colIndex, len(orderedColumns)-1), blankAfter=0)
		l, r = orderedColumns[colIndex:colIndex+2]
		squeezable = False
		for seq in r.positions.keys():
			if seq not in l.positions:
				squeezable = True
				break
		if not squeezable:
			colIndex += 1
			continue

		gapInfo = {}
		for seq in chains:
			if seq in l.positions:
				gapInfo[seq] = (False, l.positions[seq], 0)
			else:
				gapInfo[seq] = (True, None, 1)

		squeezable = False
		redo = False
		rcols = 0
		for r in orderedColumns[colIndex+1:]:
			rcols += 1
			# look for indeterminate residues first, so we can
			# potentially form a single-residue column to complete
			# the squeeze
			indeterminates = False
			for seq, rightPos in r.positions.items():
				inGap, leftPos, numGaps = gapInfo[seq]
				if leftPos is None or rightPos == leftPos + 1:
					continue
				if numGaps == 0:
					indeterminates = True
					continue
				for oseq, info in gapInfo.items():
					if oseq == seq:
						continue
					inGap, pos, numGaps = info
					if inGap:
						continue
					if numGaps != 0:
						break
				else:
					# squeezable
					orderedColumns.insert(colIndex+rcols,
						Column({seq: leftPos+1}))
					redo = True
					break
				indeterminates = True

			if redo:
				break
				
			if indeterminates:
				break

			for seq, info in gapInfo.items():
				inGap, leftPos, numGaps = info
				if seq in r.positions:
					rightPos = r.positions[seq]
					if inGap:
						# closing a gap
						gapInfo[seq] = (False,
							rightPos, 1)
					else:
						# non gap
						gapInfo[seq] = (False,
							rightPos, numGaps)
				else:
					if not inGap and numGaps > 0:
						# two gaps: no-no
						break
					gapInfo[seq] = (True, leftPos, 1)

			else:
				# check if squeeze criteria fulfilled
				for inGap, leftPos, numGaps in gapInfo.values():
					if numGaps == 0:
						break
				else:
					squeezable = True
					break
				l = r
				continue
			break

		if redo:
			continue

		if not squeezable:
			colIndex += 1
			continue

		# squeeze
		replaceCols = [Column(c)
			for c in orderedColumns[colIndex:colIndex+rcols+1]]
		for i, col in enumerate(replaceCols[:-1]):
			rcol = replaceCols[i+1]
			for seq, pos in rcol.positions.items():
				if seq in col.positions:
					continue
				col.positions[seq] = pos
				del rcol.positions[seq]
			if col.value() < 0:
				break
		else:
			assert(not replaceCols[-1].positions)
			ov = 0
			for col in orderedColumns[colIndex:colIndex+rcols+1]:
				ov += col.participation()
			nv = 0
			for col in replaceCols[:-1]:
				nv += col.participation()
			if ov >= nv:
				colIndex += 1
				continue
			orderedColumns[colIndex:colIndex+rcols+1] = \
							replaceCols[:-1]
			if colIndex > 0:
				colIndex -= 1
			continue
		colIndex += 1

	replyobj.status("%sComposing alignment\n" % statusPrefix, blankAfter=0)
	for col in orderedColumns:
		for seq, offset in col.positions.items():
			curPos = current[seq]
			diff = offset - curPos
			if diff < 2:
				continue
			if circular and seq.circular:
				if curPos >= len(seq):
					frag = seq[curPos-len(seq)+1:
							offset-len(seq)]
				elif offset >= len(seq):
					frag = seq[curPos+1:]
					frag += seq[:offset-len(seq)]
				else:
					frag = seq[curPos+1:offset]
			else:
				frag = seq[curPos+1:offset]
			clone[seq].append(frag)

			gap = gapChar * (diff - 1)
			for cseq in clone.values():
				if cseq == clone[seq]:
					continue
				cseq.append(gap)

		for seq in chains:
			try:
				offset = col.positions[seq]
				if circular and seq.circular \
				and offset >= len(seq):
					char = seq[offset-len(seq)]
				else:
					char = seq[offset]
			except KeyError:
				clone[seq].append(gapChar)
				continue
			clone[seq].append(char)
			current[seq] = offset

	for seq, offset in current.items():
		if circular and seq.circular:
			if offset < 2 * len(seq) - 1:
				if offset < len(seq) - 1:
					frag = seq[offset+1:] + seq[:]
				else:
					frag = seq[offset-len(seq)+1:]
			else:
				continue
		else:
			if offset == len(seq) - 1:
				continue
			frag = seq[offset+1:]
		gap = gapChar * len(frag)
		for cseq in clone.values():
			if cseq == clone[seq]:
				cseq.append(frag)
			else:
				cseq.append(gap)

	clones = clone.values()
	from chimera.misc import oslModelCmp
	clones.sort(lambda a, b: oslModelCmp(a.molecule.oslIdent(),
						b.molecule.oslIdent()))
	replyobj.status("%sDone\n" % statusPrefix)
	return clones

def _check(info, order, chains):
	equiv = {}
	for seq in chains:
		equiv[seq] = [None, None, None]
	todo = []
	for seq, pos in info.items():
		equiv[seq] = [pos-1, pos, pos+1]
		seqCols = order[seq]
		if not seqCols:
			continue
		for i, col in enumerate(seqCols):
			if col.positions[seq] >= pos:
				todo.append((seqCols[:i], -1))
				break
		else:
			todo.append((seqCols, -1))
			continue
		for j in range(i, len(seqCols)):
			col = seqCols[j]
			if col.positions[seq] > pos:
				if j > i:
					todo.append((seqCols[i:j], 0))
				break
		else:
			todo.append((seqCols[i:], 0))
			continue
		todo.append((seqCols[j:], 1))
	while todo:
		cols, rel = todo.pop()
		for col in cols:
			for cseq, cpos in col.positions.items():
				eqseq = equiv[cseq]
				eq = eqseq[rel+1]
				if eq is not None \
				and cmp(cpos, eq) == rel:
					continue
				seqCols = order[cseq]
				if rel == 0:
					if eq is not None:
						return False
					if (eqseq[0] is not None \
					and eqseq[0] >= cpos) \
					or (eqseq[2] is not None \
					and eqseq[2] <= cpos):
						return False
					eqseq[1] = cpos
					for i, ccol in enumerate(seqCols):
						ccolpos = ccol.positions[cseq]
						if ccolpos > cpos:
							i = len(seqCols)
							break
						if ccolpos == cpos:
							break
					else:
						i = len(seqCols)
					for j in range(i, len(seqCols)):
						ccol = seqCols[j]
						if ccol.positions[cseq] > cpos:
							break
					else:
						j = len(seqCols)
					tdlist = seqCols[i:j]
					if tdlist:
						tdlist.remove(col)
					if tdlist:
						todo.append((tdlist, 0))
					continue
				test = equiv[cseq][1]
				if test is None:
					test = equiv[cseq][1-rel]
				if test is not None \
				and cmp(cpos, test) != rel:
					return False
				if rel < 0:
					if eq is None:
						i = 0
					else:
						for i, ccol in enumerate(seqCols):
							if ccol.positions[cseq] > eq:
								break
						else:
							i = len(seqCols)
					for j in range(i, len(seqCols)):
						ccol = seqCols[j]
						if ccol.positions[cseq] > cpos:
							break
					else:
						j = len(seqCols)
					equiv[cseq][rel+1] = cpos
					tdlist = seqCols[i:j]
					if tdlist:
						tdlist.remove(col)
					if tdlist:
						todo.append((tdlist, rel))
				else:
					if eq is None:
						i = len(seqCols) - 1
					else:
						en = list(enumerate(seqCols))
						en.reverse()
						for i, ccol in en:
							if ccol.positions[cseq] < eq:
								break
						else:
							i = -1
					for j in range(i, -1, -1):
						ccol = seqCols[j]
						if ccol.positions[cseq] < cpos:
							j += 1
							break
					else:
						j = 0
					equiv[cseq][rel+1] = cpos
					tdlist = seqCols[j:i+1]
					if tdlist:
						tdlist.remove(col)
					if tdlist:
						todo.append((tdlist, rel))
	return True

def findPruneCrosslinks(allLinks, pairings, seq1, seq2,
			linkList, links1, links2, tag="", statusPrefix=""):
	replyobj.status("%sFinding crosslinks %s\n" % (statusPrefix, tag),
							blankAfter=0)

	# find crossings
	ends = []
	seq2links = []
	for links in links2:
		ends.append(len(seq2links))
		seq2links.extend(links)
	l2lists = []
	for end in ends:
		l2lists.append(seq2links[:end])
	for link1 in linkList:
		i1 = link1.info[0].pos
		i2 = link1.info[1].pos
		for link2 in l2lists[i2]:
			if link2.info[0].pos <= i1:
				continue
			link1.crosslinks.append(link2)
			link2.crosslinks.append(link1)
			link1.penalty += link2.val
			link2.penalty += link1.val

	replyobj.status("%sPruning crosslinks %s\n" % (statusPrefix, tag),
							blankAfter=0)
	while linkList:
		pen = pos = None
		for i, x in enumerate(linkList):
			if pen is None or x.penalty > pen:
				pos = i
				pen = x.penalty
		if pen <= 0.0001:
			break
		link = linkList.pop(pos)
		links1[link.info[0].pos].remove(link)
		links2[link.info[1].pos].remove(link)
		for clink in link.crosslinks:
			clink.penalty -= link.val
	for link in linkList:
		delattr(link, "crosslinks")
		delattr(link, "penalty")

	p1 = pairings[seq1]
	for i, l in enumerate(links1):
		p1[i].extend(l)
		allLinks.extend(l)
	p2 = pairings[seq2]
	for i, l in enumerate(links2):
		p2[i].extend(l)
