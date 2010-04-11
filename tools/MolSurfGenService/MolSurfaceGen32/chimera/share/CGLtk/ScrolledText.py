import Tkinter as Tk
from AuxWidgets import WidgetWrapper, _splitCnf
from Tkinter import _cnfmerge

#
# ScrolledText is a Text with automatic scrollbars on the right
# and bottom (left is arguably better, but everyone is used to the
# right side now). To avoid problems with the infinite scrollbar
# mapping/unmapping the scrollbars stick until the text is 'clear'ed.
# The clear method handles read-only text.  This widget works for both
# fixed width fonts and variable width fonts.  In Tk 8.4.13, using the
# <<Modified>> virtual event to tell when the text widget is empty,
# doesn't work.
#
class ScrolledText(WidgetWrapper, Tk.Text):
	def __init__(self, master=None, cnf={}, **kw):
		WidgetWrapper.__init__(self, master)
		xscrollCnf, cnf = _splitCnf('xscrollbar_', _cnfmerge((cnf, kw)))
		yscrollCnf, cnf = _splitCnf('yscrollbar_', cnf)
		self._xscroll = Tk.Scrollbar(self.super, xscrollCnf,
				orient=Tk.HORIZONTAL, command=self.xview)
		self._yscroll = Tk.Scrollbar(self.super, yscrollCnf,
							command=self.yview)
		Tk.Text.__init__(self, self.super, cnf, wrap=Tk.NONE,
				xscrollcommand=self._xset,
				yscrollcommand=self._yset)
		self._hasXScroll = False
		self._hasYScroll = False
		self._skipReset = False
		self.bind('<Configure>', self._reset)
		#self.bind('<<Modified>>', self._monitor)

		self.super.grid_rowconfigure(0, weight=1)
		self.super.grid_columnconfigure(0, weight=1)

		Tk.Text.grid(self, row=0, column=0, sticky='nesw')
		#self._xscroll.grid(row=1, column=0, sticky='new')
		#self._yscroll.grid(row=0, column=1, sticky='nes')

	def clear(self):
		state = self.cget('state')
		if state == Tk.DISABLED:
			self.config(state=Tk.NORMAL)
		self.delete(1.0, Tk.END)
		if state == Tk.DISABLED:
			self.config(state=Tk.DISABLED)
		self._reset()

	def _monitor(self, event):
		# doesn't work because Tk calls this too early on deletions
		# so index only goes down to 1.1 instead of 1.0.
		#Tkinter bug: modified = self.edit_modified()
		modified = int(self.tk.call(self._w, 'edit', 'modified'))
		if not modified:
			return
		if self.index('end - 1c') == '1.0':
			self._reset()
		self.edit_modified('false')

	def _reset(self, event=None):
		self.after_idle(self.see, 'insert')
		if self._skipReset:
			self._skipReset = False
			return
		self._skipReset = True
		self._hasXScroll = False
		self._xscroll.grid_forget()
		self._hasYScroll = False
		self._yscroll.grid_forget()
		#print 'done _reset'

	def _xset(self, first, last):
		mapped = self.winfo_ismapped()
		#print '_xset', first, last, self._hasXScroll
		if float(first) != 0.0 or float(last) != 1.0:
			if not self._hasXScroll:
				self._hasXScroll = True
				if mapped:
					# keep top-level window from being
					# resized automatically after scroll
					# bar is mapped
					self._skipReset = True
					top = self.winfo_toplevel()
					top.wm_geometry(top.wm_geometry())
				self._xscroll.grid(row=1, column=0, stick='new')
		self._xscroll.set(first, last)

	def _yset(self, first, last):
		mapped = self.winfo_ismapped()
		#print '_yset', first, last, self._hasYScroll
		if float(first) != 0.0 or float(last) != 1.0:
			if not self._hasYScroll:
				self._hasYScroll = True
				if mapped:
					# keep top-level window from being
					# resized automatically after scroll
					# bar is mapped
					self._skipReset = True
					top = self.winfo_toplevel()
					top.wm_geometry(top.wm_geometry())
				self._yscroll.grid(row=0, column=1, stick='nes')
		self._yscroll.set(first, last)

#
# FixedScrolledText is a Text with automatic scrollbars on the right and bottom
# (left is arguably better, but everyone is used to the right side now).
# Only works well for fixed width fonts.
#
class FixedScrolledText(WidgetWrapper, Tk.Text):
	def __init__(self, master=None, cnf={}, **kw):
		WidgetWrapper.__init__(self, master)
		xscrollCnf, cnf = _splitCnf('xscrollbar_', _cnfmerge((cnf, kw)))
		yscrollCnf, cnf = _splitCnf('yscrollbar_', cnf)
		self._xscroll = Tk.Scrollbar(self.super, xscrollCnf,
				orient=Tk.HORIZONTAL, command=self.xview)
		self._yscroll = Tk.Scrollbar(self.super, yscrollCnf,
							command=self.yview)
		Tk.Text.__init__(self, self.super, cnf, wrap=Tk.NONE,
				xscrollcommand=self._xscroll.set,
				yscrollcommand=self._yscroll.set)
		self._numLines = 0
		self._maxLineLen = 0
		import tkFont
		fontname = self.cget('font')
		font = tkFont.Font(self, fontname)
		self._linespace = font.metrics('linespace')
		self._charwidth = font.measure('0')
		self._offset = int(self.cget('borderwidth')) \
					+ int(self.cget('padx')) \
					+ int(self.cget('selectborderwidth')) \
					+ int(self.cget('highlightthickness'))
		self._offset *= 2 # both sides
		self._inShow = False
		self.bind('<<Modified>>', self._modified)
		self.bind('<Configure>', self._showScrollbars)

		# Set horizontal scroll bar to be the same height as one line
		# so only whole lines are visible.  Set the width of the
		# vertical scroll bar the same for consistency.
		barSize = self._linespace - 2 * (
				int(self._xscroll.cget('borderwidth'))
				+ int(self._xscroll.cget('highlightthickness')))
		self._xscroll.configure(width=barSize)
		self._yscroll.configure(width=barSize)
		self.super.grid_rowconfigure(0, weight=1)
		self.super.grid_columnconfigure(0, weight=1)

		Tk.Text.grid(self, row=0, column=0, sticky='nesw')
		#self._xscroll.grid(row=1, column=0, sticky='new')
		#self._yscroll.grid(row=0, column=1, sticky='nes')

	def _showScrollbars(self, *ignore):
		if self._inShow:
			return
		self._inShow = True
		width = (self.winfo_width() - self._offset) / self._charwidth
		height = (self.winfo_height() - self._offset) / self._linespace
		#print 'width, height:', width, height
		if self._numLines <= height:
			if self._yscroll.winfo_ismapped():
				self._yscroll.grid_forget()
		else:
			if not self._yscroll.winfo_ismapped():
				self._yscroll.grid(row=0, column=1, stick='nes')
		if self._maxLineLen <= width:
			if self._xscroll.winfo_ismapped():
				self._xscroll.grid_forget()
		else:
			if not self._xscroll.winfo_ismapped():
				self._xscroll.grid(row=1, column=0, stick='new')
		#self.see('insert') -- causes core dump in Tk!
		self._inShow = False
		self.after_idle(self.see, 'insert')

	def _modified(self, event):
		#Tkinter bug: modified = self.edit_modified()
		modified = int(self.tk.call(self._w, 'edit', 'modified'))
		if not modified:
			return
		#print 'modified', vars(event)
		text = self.get('1.0', 'end')
		lines = text.split('\n')
		self._numLines = len(lines) - 1
		self._maxLineLen = max([len(l) for l in lines])
		if self.winfo_ismapped():
			# keep top-level window from being resized
			# automatically after scroll bar(s) is(are) mapped
			top = self.winfo_toplevel()
			top.wm_geometry(top.wm_geometry())
			self._showScrollbars()
		self.edit_modified('false')
		#print 'numLines, maxLineLen:', self._numLines, self._maxLineLen
		#print 'lines:', repr(lines)

	def clear(self):
		state = self.cget('state')
		if state == Tk.DISABLED:
			self.config(state=Tk.NORMAL)
		self.delete(1.0, Tk.END)
		if state == Tk.DISABLED:
			self.config(state=Tk.DISABLED)

if __name__ == '__main__':
	t = ScrolledText(width=20, height=4)
	t.pack(expand=True, fill=Tk.BOTH)
	t.mainloop()
