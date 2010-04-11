# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Cluster.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter, Pmw
from chimera.baseDialog import ModelessDialog
from chimera import UserError
from CGLtk.color import colorRange, rgba2tk

class ClusterStarter(ModelessDialog):
	title = "Get Clustering Parameters"

	def __init__(self, movie):
		self.movie = movie
		movie.subdialogs.append(self)
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		from chimera.tkoptions import IntOption, BooleanOption, \
							FloatOption
		Tkinter.Label(parent, text="Cluster trajectory",
				relief="ridge", bd=4).grid(row=0,
				column=0, columnspan=2, sticky="ew")

		startFrame = self.movie.startFrame
		endFrame = self.movie.endFrame
		self.startFrame = IntOption(parent, 1, "Starting frame",
			startFrame, None, min=startFrame, max=endFrame, width=6)

		numFrames = endFrame - startFrame + 1
		defStride = 1 + int(numFrames/300)
		self.stride = IntOption(parent, 2, "Step size", defStride,
			None, min=1, max=numFrames, width=3)

		self.endFrame = IntOption(parent, 3, "Ending frame", endFrame,
			None, min=startFrame, max=endFrame, width=6)

		self.useSel = BooleanOption(parent, 4, "Cluster based on "
				"current selection, if any", True, None)

		self.ignoreBulk = BooleanOption(parent, 5, "Ignore solvent/"
							"ions", True, None)
		self.ignoreHyds = BooleanOption(parent, 6, "Ignore hydrogens",
							True, None)
	def Apply(self):
		startFrame = self.startFrame.get()
		stride = self.stride.get()
		endFrame = self.endFrame.get()
		if endFrame <= startFrame:
			self.enter()
			raise UserError("Start frame must be less"
							" than end frame")
		if startFrame < self.movie.startFrame \
		or endFrame > self.movie.endFrame:
			self.enter()
			raise UserError("Start or end frame outside"
							" of trajectory")
		ClusterDialog(self.movie, startFrame, self.stride.get(),
			endFrame, self.useSel.get(), self.ignoreBulk.get(),
			self.ignoreHyds.get())

class ClusterDialog(ModelessDialog):
	oneshot = True
	provideStatus = True
	buttons = ("Close",)
	title = "Clustering"

	def __init__(self, movie, startFrame, stride, endFrame, useSel,
						ignoreBulk, ignoreHyds):
		self.movie = movie
		self.movie.subdialogs.append(self)
		self.startFrame = startFrame
		self.stride = stride
		self.endFrame = endFrame
		self.useSel = useSel
		self.ignoreBulk = ignoreBulk
		self.ignoreHyds = ignoreHyds
		ModelessDialog.__init__(self)

	def Close(self):
		if self._computing:
			self._abort = True
			return
		self.movie.subdialogs.remove(self)
		ModelessDialog.Close(self)

	def destroy(self):
		# calling ModelessDialog.Close causes recursion
		ModelessDialog.destroy(self)

	def fillInUI(self, parent):
		from chimera.match import matchPositions
		from chimera import numpyArrayFromAtoms
		from chimera import selection, UserError

		self._computing = False

		# load needed coord sets...
		frameNums = range(self.startFrame, self.endFrame+1, self.stride)
		for frameNum in frameNums:
			if not self.movie.findCoordSet(frameNum):
				self.status("loading frame %d" % frameNum)
				self.movie._LoadFrame(frameNum,
							makeCurrent=False)

		# compute RMSDs
		from analysis import analysisAtoms
		try:
			atoms = analysisAtoms(self.movie, self.useSel,
					self.ignoreBulk, self.ignoreHyds)
		except UserError:
			self.Close()
			raise

		self.buttonWidgets['Close'].configure(text="Abort")
		numFrames = len(frameNums)
		self.status("Fetching %d coordinate arrays" % numFrames)
		numpyArrays = {}
		from time import time
		t0 = time()
		for i, fn in enumerate(frameNums):
			numpyArrays[fn] = numpyArrayFromAtoms(atoms,
						self.movie.findCoordSet(fn))
			self._computing = True
			self._abort = False
			parent.update() # allow Abort button to function
			self._computing = False
			if self._abort:
				parent.after_idle(self.Close)
				return
			if i == numFrames - 1:
				self.status("Fetched %d coordinate arrays"
									% (i+1))
			else:
				elapsed = time() - t0
				perSec = elapsed / (i+1)
				remaining = perSec * (numFrames - (i+1))
				self.status("Fetched %d of %d coordinate arrays"
					"\nAbout %.1f minutes remaining" %
					(i+1, numFrames, remaining / 60.0))
		t0 = time()
		totalRMSDs = numFrames * (numFrames - 1) / 2
		self.status("Computing %d RMSDs" % totalRMSDs)
		from EnsembleMatch.distmat import DistanceMatrix
		fullDM = DistanceMatrix(numFrames)
		sameAs = {}
		for i, frame1 in enumerate(frameNums):
			na1 = numpyArrays[frame1]
			for j, frame2 in enumerate(frameNums[i+1:]):
				na2 = numpyArrays[frame2]
				rmsd = matchPositions(na1, na2)[1]
				fullDM.set(i, i+j+1, rmsd)
				if rmsd == 0.0:
					sameAs[frame2] = frame1
			self._computing = True
			self._abort = False
			parent.update() # allow Abort button to function
			self._computing = False
			if self._abort:
				parent.after_idle(self.Close)
				return
			numComputed = totalRMSDs - ((numFrames - (i+1)) *
							(numFrames - (i+2))) / 2
			if numComputed == totalRMSDs:
				self.status("Computed %d RMSDs" % totalRMSDs)
			else:
				elapsed = time() - t0
				perSec = elapsed / numComputed
				remaining = perSec * (totalRMSDs - numComputed)
				if remaining < 50:
					timeEst = "%d seconds" % int(
							remaining + 0.5)
				else:
					timeEst = "%.1f minutes" % (
							remaining / 60.0)
				self.status("Computed %d of %d RMSDs\n"
					"About %s remaining" % (numComputed,
					totalRMSDs, timeEst))
		self.status("Generating clusters")
		self.buttonWidgets['Close'].configure(text="Close")
		if not sameAs:
			dm = fullDM
			reducedFrameNums = frameNums
			indexMap = range(len(frameNums))
		elif len(sameAs) == numFrames - 1:
			raise UserError("All frames to cluster are identical!")
			self.Close()
		else:
			dm = DistanceMatrix(numFrames - len(sameAs))
			reducedFrameNums = []
			indexMap = []
			for i, fn in enumerate(frameNums):
				if fn in sameAs:
					continue
				reducedFrameNums.append(fn)
				indexMap.append(i)
			for i in range(len(reducedFrameNums)):
				mapi = indexMap[i]
				for j in range(i+1, len(reducedFrameNums)):
					mapj = indexMap[j]
					dm.set(i, j, fulldm.get(mapi, mapj))
		from EnsembleMatch.nmrclust import NMRClust
		clustering = NMRClust(dm)
		self.clusterMap = {}
		self.representatives = []
		self.clusters = []
		unsortedClusters = [(c, clustering.representative(c))
						for c in clustering.clusters]
		# sort the clusters so that the coloring is reproducible
		# while trying to avoid using adjacent colors for
		# adjacent clusters
		clusters = [unsortedClusters.pop()]
		while unsortedClusters:
			bestCluster = bestVal = None
			for uc in unsortedClusters:
				val = abs(uc[-1] - clusters[-1][-1])
				if len(clusters) > 1:
					val += 0.5 * abs(uc[-1]
							- clusters[-2][-1])
				if len(clusters) > 2:
					val += 0.25 * abs(uc[-1]
							- clusters[-3][-1])
				if bestVal == None or val > bestVal:
					bestCluster = uc
					bestVal = val
			unsortedClusters.remove(bestCluster)
			clusters.append(bestCluster)
		colors = colorRange(len(clusters))
		for c, rep in clusters:
			cluster = Cluster()
			cluster.color = colors.pop()
			self.clusters.append(cluster)
			cluster.representative = reducedFrameNums[rep]
			cluster.members = []
			for m in c.members():
				f = reducedFrameNums[m]
				self.clusterMap[f] = cluster
				cluster.members.append(f)
		for dup, base in sameAs.items():
			c = self.clusterMap[base]
			self.clusterMap[dup] = c
			c.members.append(dup)
		self.status("%d clusters" % len(self.clusters))

		from CGLtk.Table import SortableTable
		self.table = SortableTable(parent)
		self.table.addColumn("Color", "color", format=(False, False),
							titleDisplay=False)
		membersCol = self.table.addColumn("Members",
				"lambda c: len(c.members)", format="%d")
		self.table.addColumn("Representative Frame", "representative",
								format="%d")
		self.table.setData(self.clusters)
		self.table.launch(browseCmd=self.showRep)
		self.table.sortBy(membersCol)
		self.table.sortBy(membersCol) # to get descending order
		self.table.grid(sticky="nsew")
		self.timeLine = Pmw.ScrolledCanvas(parent, canvas_height="0.5i")
		self.timeLine.grid(row=1, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		self.zoom = 2.0
		self.drawTimeLine()

	def drawTimeLine(self, width=None):
		if width == None:
			width = 3.0
		tl = self.timeLine
		for item in tl.find_all():
			tl.delete(item)
		for c in self.clusters:
			c.canvasItems = []
			c.canvas = tl
		frameNums = range(self.startFrame, self.endFrame+1, self.stride)
		cluster = startFrame = None
		f2x = self._frame2x
		height = 22
		for fn in frameNums:
			c = self.clusterMap[fn]
			if c == cluster:
				continue
			if cluster != None:
				tkColor = rgba2tk(cluster.color)
				cluster.canvasItems.append(tl.create_rectangle(
					f2x(startFrame), 0, f2x(fn)-1,
					height, fill=tkColor, outline=tkColor))
			cluster = c
			startFrame = fn
		tkColor = rgba2tk(cluster.color)
		cluster.canvasItems.append(tl.create_rectangle(f2x(startFrame),
					0, f2x(frameNums[-1]+self.stride)-1,
					height, fill=tkColor, outline=tkColor))
		for c in self.clusters:
			rep = c.representative
			tkColor = rgba2tk(c.color)
			c.canvasItems.append(tl.create_rectangle(
				f2x(rep), 0, f2x(rep+self.stride)-1,
				-0.5*height, fill=tkColor, outline=tkColor))
		tl.resizescrollregion()

	def showRep(self, clusters):
		self.movie.currentFrame.set(clusters[0].representative)
		self.movie.LoadFrame()

	def _frame2x(self, fn):
		return int(self.zoom * (fn-self.startFrame) / self.stride + 0.5)

class Cluster(object):
	def getColor(self):
		return self.__color
	def setColor(self, color):
		self.__color = color
		if hasattr(self, 'canvasItems'):
			tkColor = rgba2tk(color)
			for i in self.canvasItems:
				self.canvas.itemconfigure(i, fill=tkColor,
							outline=tkColor)
	color = property(getColor, setColor)

