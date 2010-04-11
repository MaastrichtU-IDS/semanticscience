#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Sash.py 26655 2009-01-07 22:02:30Z gregc $


import Tkinter
Tk = Tkinter
from Tkinter import _cnfmerge
from SimpleDialog import SimpleDialog
import sys

IPS = 4		# Inter-pane spacing.  Must be a multiple
		# of 2 because when we add panes, we will
		# pad them with IPS/2 pixels to make sure
		# that we get exactly the right initial
		# window size

class CollapsiblePane(Tk.Frame):
	"""
	CollapsiblePane is a frame that has a Checkbutton at the
	top which controls whether the rest of the frame is displayed.
	CollapsiblePane instances should be children of Sash (below).
	"""
	def __init__(self, master=None, title='Untitled',
			titleFont=None, collapsed=0, **kw):
		Tk.Frame.__init__(self, master, kw, bd=2, relief=Tk.SUNKEN)
		buttonCnf = { 'anchor':Tk.W, 'bd':2, 'relief':Tk.RIDGE,
				'text':title, 'onvalue':1, 'offvalue':0}
		if collapsed:
			buttonCnf['command'] = self.show
		else:
			buttonCnf['command'] = self.hide
		if titleFont != None:
			buttonCnf['font'] = titleFont
		self.state = Tk.IntVar(master=self.master)
		buttonCnf['variable'] = self.state
		self.button = Tk.Checkbutton(self, buttonCnf)
		self.button.pack(side=Tk.TOP, fill=Tk.X)
		self.frame = Tk.Frame(self, bd=2, relief=Tk.SUNKEN)
		if not collapsed:
			self.frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=Tk.TRUE)
			self.button.select()
		self.paneCollapsed = collapsed
		self.paneMinHeight = self.button.winfo_reqheight() + \
						int(str(self.button['bd'])) * 2
		self.paneMinWidth = self.button.winfo_reqwidth()

	def hide(self):
		self.paneCollapsed = Tk.TRUE
		self.button['command'] = self.show
		if not hasattr(self, 'paneHeight'):
			# Must be during setup (before being shown on screen)
			if self.state.get():
				self.frame.forget()
			self.button.deselect()
			return
		self.savePaneHeight = self.paneHeight
		self.paneHeight = self.winfo_height() - \
					self.frame.winfo_height()
		self.frame.forget()
		top = self.winfo_toplevel()
		ht = top.winfo_height() - self.savePaneHeight + \
			self.paneHeight
		wd = top.winfo_width()
		top.geometry('%dx%d' % (wd, ht))

	def show(self):
		self.paneCollapsed = Tk.FALSE
		self.button['command'] = self.hide
		if not hasattr(self, 'paneHeight'):
			# Must be during setup (before being shown on screen)
			if not self.state.get():
				self.frame.pack(side=Tk.TOP, fill=Tk.BOTH,
						expand=Tk.TRUE)
			self.button.select()
			return
		if not hasattr(self, 'savePaneHeight'):
			# Must be because we started hidden
			self.savePaneHeight = self.paneHeight + \
						self.frame.winfo_reqheight()
		self.frame.pack(side=Tk.TOP, fill=Tk.BOTH, expand=Tk.TRUE,
				after=self.button)
		top = self.winfo_toplevel()
		ht = top.winfo_height() - self.paneHeight + \
			self.savePaneHeight
		self.paneHeight = self.savePaneHeight
		wd = top.winfo_width()
		top.geometry('%dx%d' % (wd, ht))

def _isCollapsed(pane):
	if not _isVisible(pane):
		return 1
	if not hasattr(pane, 'paneCollapsed'):
		return 0
	return pane.paneCollapsed

def _isVisible(pane):
	if not hasattr(pane, 'paneVisible'):
		return 1
	return pane.paneVisible

class Sash(Tk.Frame):
	"""
	Sash is a Frame that contains several horizontally spanning Pane's
	(see above).  When any Pane changes in size, the Sash will handle
	the reconfiguration of the entire set of Panes.
	"""
	def __init__(self, master=None, orient=Tk.VERTICAL, cnf={}, **kw):
		if orient == Tk.VERTICAL:
			self.orientation = Tk.VERTICAL
		elif orient == Tk.HORIZONTAL:
			self.orientation = Tk.HORIZONTAL
		else:
			raise ValueError, 'unknown orientation'
		if self.orientation is Tk.VERTICAL:
			self._buttonDrag = self._buttonDragVertical
			cursor = 'sb_v_double_arrow'
		else:
			self._buttonDrag = self._buttonDragHorizontal
			cursor = 'sb_h_double_arrow'
		cnf = _cnfmerge((cnf, kw))
		Tk.Frame.__init__(self, master, cnf, cursor=cursor)
		self.needResize = self.master is self.winfo_toplevel()
		self.paneList = []
		self.bind('<Configure>', self._computeSize)
		self.bind('<ButtonPress-1>', self._buttonPress)
		self.bind('<ButtonRelease-1>', self._buttonRelease)

	def destroy(self):
		del self._buttonDrag
		del self.paneList
		self.reconfigure = None
		Tk.Frame.destroy(self)

	def addPane(self, pane, where=-1):
		pane['cursor'] = 'arrow'
		if self.orientation is Tk.VERTICAL:
			side = Tk.TOP
			px = 0
			py = self.paneList and IPS / 2 or 0
		else:
			side = Tk.LEFT
			px = self.paneList and IPS / 2 or 0
			py = 0
		if where < 0:
			pane.pack(side=side, expand=Tk.TRUE, fill=Tk.BOTH,
					padx=px, pady=py)
			self.paneList.append(pane)
		else:
			pane.pack(side=side, expand=Tk.TRUE, fill=Tk.BOTH,
					padx=px, pady=py,
					after=self.paneList[where])
			self.paneList.insert(where, pane)

	def setVisible(self, pane, flag):
		if not pane in self.paneList:
			return
		pane.paneVisible = flag
		if pane.winfo_ismapped():
			self.reconfigure()

	def _computeSize(self, *args):
		if self.orientation is Tk.VERTICAL:
			height = IPS * len(self.paneList) - IPS
			width = 0
			self.reconfigure = self._reconfigureVertical
		else:
			height = 0
			width = IPS * len(self.paneList) - IPS
			self.reconfigure = self._reconfigureHorizontal
		for p in self.paneList:
			ht = p.winfo_reqheight()
			wd = p.winfo_reqwidth()
			if self.orientation is Tk.VERTICAL:
				height = height + ht
				if wd > width:
					width = wd
			else:
				if ht > height:
					height = ht
				width = width + wd
			p.paneHeight = ht
			p.paneWidth = wd
			if not hasattr(p, 'paneMinHeight'):
				p.paneMinHeight = 1
			if not hasattr(p, 'paneMinWidth'):
				p.paneMinWidth = 1
		for p in self.paneList:
			p.pack_forget()
		self.bind('<Configure>', self.reconfigure)
		self.reconfigure()

	def _reconfigureVertical(self, *args):
		totalHeight = 0.0
		numPanes = 0
		for p in self.paneList:
			if _isVisible(p):
				totalHeight = totalHeight + p.paneHeight
				numPanes = numPanes + 1
		myHeight = float(self.winfo_height())
		availableHeight = myHeight - IPS * numPanes + IPS
		ratio = availableHeight / totalHeight
		self.gapList = []
		y = 0.0
		for p in self.paneList:
			if not _isVisible(p):
				ht = 0
				p.paneHeight = p.paneHeight * ratio
			else:
				ht = p.paneHeight * ratio
				p.paneHeight = ht
			p.place(relx=0, relwidth=1, y=y, height=ht)
			y = y + ht + IPS
			self.gapList.append(y)

	def _reconfigureHorizontal(self, *args):
		totalWidth = 0.0
		numPanes = 0
		for p in self.paneList:
			if _isVisible(p):
				totalWidth = totalWidth + p.paneWidth
				numPanes = numPanes + 1
		myWidth = float(self.winfo_width())
		availableWidth = myWidth - IPS * numPanes + IPS
		ratio = availableWidth / totalWidth
		self.gapList = []
		x = 0.0
		for p in self.paneList:
			if not _isVisible(p):
				wd = 0
				p.paneWidth = p.paneWidth * ratio
			else:
				wd = p.paneWidth * ratio
				p.paneWidth = wd
			p.place(rely=0, relheight=1, x=x, width=wd)
			x = x + wd + IPS
			self.gapList.append(x)

	def _buttonPress(self, event):
		if self.orientation is Tk.VERTICAL:
			crd = event.y
		else:
			crd = event.x
		gapIndex = -1
		for i in range(len(self.gapList)):
			if crd < self.gapList[i]:
				gapIndex = i
				break
		if gapIndex == -1:
			raise SystemError, 'cannot identify sash gap'
		paneAbove = None
		for above in range(gapIndex, -1, -1):
			pane = self.paneList[above]
			if not _isCollapsed(pane):
				paneAbove = pane
				break
		if paneAbove is None:
			d = SimpleDialog(self.winfo_toplevel(),
				text='There is no adjustable pane above',
				buttons=['Okay'],
				title='User Error')
			d.go()
			return
		paneBelow = None
		for below in range(gapIndex + 1, len(self.paneList)):
			pane = self.paneList[below]
			if not _isCollapsed(pane):
				paneBelow = pane
				break
		if paneBelow is None:
			d = SimpleDialog(self.winfo_toplevel(),
				text='There is no adjustable pane below',
				buttons=['Okay'],
				title='User Error')
			d.go()
			return
		self.adjustAbove = paneAbove
		self.adjustBelow = paneBelow
		self.drag = crd
		self.bind('<Motion>', self._buttonDrag)

	def _buttonRelease(self, event):
		self.gapIndex = -1
		self.unbind('<Motion>')

	def _buttonDragVertical(self, event):
		delta = event.y - self.drag
		if delta < 2 and delta > -2:
			return
		aboveHt = self.adjustAbove.paneHeight + delta
		belowHt = self.adjustBelow.paneHeight - delta
		if aboveHt < self.adjustAbove.paneMinHeight \
		or belowHt < self.adjustBelow.paneMinHeight:
			return
		self.adjustAbove.paneHeight = aboveHt
		self.adjustBelow.paneHeight = belowHt
		self.reconfigure()
		self.drag = event.y

	def _buttonDragHorizontal(self, event):
		delta = event.x - self.drag
		if delta < 2 and delta > -2:
			return
		aboveWd = self.adjustAbove.paneWidth + delta
		belowWd = self.adjustBelow.paneWidth - delta
		if aboveWd < self.adjustAbove.paneMinWidth \
		or belowWd < self.adjustBelow.paneMinWidth:
			return
		self.adjustAbove.paneWidth = aboveWd
		self.adjustBelow.paneWidth = belowWd
		self.reconfigure()
		self.drag = event.x

if __name__ == '__main__':
	f = Sash()
	f.pack(expand=Tk.TRUE, fill=Tk.BOTH)

	p = CollapsiblePane(f, collapsed=1)
	f.addPane(p)
	e = Tk.Entry(p.frame, width=20)
	e.pack(side=Tk.TOP, expand=Tk.TRUE, fill=Tk.BOTH)

	b = Tk.Button(f, text='Quit', command=f.quit)
	f.addPane(b)

	e = Tk.Text(f, width=20, height=5)
	f.addPane(e, where=0)

	f.mainloop()
