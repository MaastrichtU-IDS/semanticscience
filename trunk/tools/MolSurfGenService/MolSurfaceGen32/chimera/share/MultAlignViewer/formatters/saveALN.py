# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: saveALN.py 26655 2009-01-07 22:02:30Z gregc $


extension = ".aln"
from MultAlignViewer.parsers.readALN import fileType, extensions
globs = ["*" + ext for ext in extensions]
from chimera.Sequence import Sequence, clustalStrongGroups, clustalWeakGroups

LINELEN = 50

def save(fileObj, mav, seqs, fileMarkups):
	print>>fileObj, "CLUSTAL W ALN saved from UCSF Chimera/MultAlignViewer"
	print>>fileObj, ""

	maxName = 0
	for seq in seqs:
		maxName = max(maxName, len(seq.name))
	nameFormat = "%%-%ds" % (maxName+5,)

	for start in range(0, len(seqs[0]), LINELEN):
		end = min(len(seqs[0]), start + LINELEN)
		
		for seq in seqs:
			name = seq.name.replace(' ', '_')
			tempSeq = Sequence("temp")
			tempSeq.append(seq[start:end])
			if len(tempSeq.ungapped(_raw=True)) == 0:
				print>>fileObj, nameFormat % name, \
						seq[start:end]
			else:
				tempSeq = Sequence("temp")
				tempSeq.append(seq[:end])
				numResidues = len(tempSeq.ungapped(_raw=True))
				print>>fileObj, nameFormat % name, \
						seq[start:end], numResidues
		conservation = []
		for pos in range(start, end):
			# completely conserved?
			first = seqs[0][pos].upper()
			if first.isupper():
				for seq in seqs[1:]:
					if seq[pos].upper() != first:
						break
				else:
					# conserved
					conservation.append("*")
					continue

			# "strongly" conserved?
			conserved = 0
			for group in clustalStrongGroups:
				for seq in seqs:
					if seq[pos].upper() not in group:
						break
				else:
					# conserved
					conserved = 1
					break
			if conserved:
				conservation.append(":")
				continue


			# "weakly" conserved?
			for group in clustalWeakGroups:
				for seq in seqs:
					if seq[pos].upper() not in group:
						break
				else:
					# conserved
					conserved = 1
					break
			if conserved:
				conservation.append(".")
				continue

			# remainder
			conservation.append(" ")
		print>>fileObj, nameFormat % " ", "".join(conservation)
		print>>fileObj, ""

