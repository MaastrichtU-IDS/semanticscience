# Eventually, this code may get incorporated into Tix.py, so
# we don't want to have "Tix." spread all over the place

from Tix import *
from Tix import _dummyScrollbar

class Grid(TixWidget):
    """Grid - Rectangular grid of display items"""

    def __init__(self, master, cnf={}, **kw):
	TixWidget.__init__(self, master, "tixGrid", ["options"], cnf, kw)

    def anchor(self, cnf={}, **kw):
        args = (self._w, "anchor") + self._options(cnf, kw)
        return self.tk.call(*args)

    def bdtype(self, x, y, xbdWidth=None, ybdWidth=None):
	if xbdWidth is None or ybdWidth is None:
	    return self.tk.call(self._w, "bdtype", x, y)
	else:
	    return self.tk.call(self._w, "bdtype", x, y, xbdWidth, ybdWidth)

    def delete(self, dim, iFrom, iTo=None):
        if iTo is not None:
	    args = (self._w, "delete", dim, iFrom, iTo)
	else:
	    args = (self._w, "delete", dim, iFrom)
        return self.tk.call(*args)

    def edit_apply(self):
        return self.tk.call(self._w, "edit", "apply")

    def edit_set(self, x, y):
        return self.tk.call(self._w, "edit", "set", x, y)

    def entrycget(self, x, y, cnf={}, **kw):
        args = (self._w, "entrycget", x, y) + self._options(cnf, kw)
        return self.tk.call(*args)

    def entryconfigure(self, x, y, cnf={}, **kw):
        args = (self._w, "entryconfigure", x, y) + self._options(cnf, kw)
        return self.tk.call(*args)

    def format(self, t, x1, y1, x2, y2, cnf={}, **kw):
        args = (self._w, "format", t, x1, y1, x2, y2) + self._options(cnf, kw)
        return self.tk.call(*args)

    def index(self, i1="", i2=""):
        return self.tk.call(self._w, "edit", "index", i1, i2)

    def move(self, dim, iFrom, iTo, offset):
        return self.tk.call(self._w, "move", iFrom, iTo, offset)

    def set(self, x, y, itemtype=None, cnf={}, **kw):
	args = (self._w, "set", x, y)
	if itemtype is not None:
	    args += ("-itemtype", itemtype)
        args += self._options(cnf, kw)
        return self.tk.call(*args)

    def size(self, dim, index, itemtype=None, cnf={}, **kw):
	args = (self._w, "size", dim, index) + self._options(cnf, kw)
        return self.tk.call(*args)

    def unset(self, x, y):
        return self.tk.call(self._w, "unset", x, y)

    def xview(self, *aList):
	args = (self._w, "xview") + aList
        return self.tk.call(*args)

    def yview(self):
	args = (self._w, "yview") + aList
        return self.tk.call(*args)

class ScrolledGrid(TixWidget):
    """ScrolledText - Text with scrollbars."""

    def __init__(self, master, cnf={}, **kw):
        TixWidget.__init__(self, master, "tixScrolledGrid",
				["options"], cnf, kw)
        self.subwidget_list["tixGrid"] = _dummyGrid(self, "grid")
        self.subwidget_list["vsb"] = _dummyScrollbar(self, "vsb")
        self.subwidget_list["hsb"] = _dummyScrollbar(self, "hsb")

class _dummyGrid(Grid, TixSubWidget):
    def __init__(self, master, name, destroy_physically=1):
        TixSubWidget.__init__(self, master, name, destroy_physically)

if __name__ == "__main__":
    import Tkinter
    bg = {
	"s-margin": "gray65",
    	"x-margin": "gray65",
    	"y-margin": "gray65",
    	"main":     "gray20",
    }

    def MakeGrid(w):
	g = ScrolledGrid(w, bd=0)
	g.pack(expand="yes", fill="both", padx=3, pady=3)
	grid = g.tixGrid
	def SimpleFormat(area, x1, y1, x2, y2, grid=grid):
	    if area == "main":
		grid.format("grid", x1, y1, x2, y2,
			    relief="raised", bd=1, bordercolor=bg[area],
			    fill=0, bg="red", xon=1, yon=1, xoff=0, yoff=0,
			    anchor="se")
	    elif area in ["x-margin", "y-margin", "s-margin"]:
		grid.format("border", x1, y1, x2, y2,
			    fill=1, relief="raised", bd=1, bg=bg[area],
			    selectbackground="gray80")
	grid.config(formatcmd=SimpleFormat)
	grid.size("col", 0, size="10char")
	grid.size("col", 1, size="auto")
	grid.size("col", 2, size="auto")
	grid.size("col", 3, size="auto")
	grid.size("col", 4, size="auto")
	grid.size("col", "default", size="5char")
	grid.size("row", "default", size="1.1char", pad0=3)

	for x in range(10):
	    for y in range(10):
		grid.set(x, y, itemtype="text", text="(%d,%d)" % (x, y))

    w = Tkinter.Frame()
    w.tk.eval('package require Tix')
    w.pack(expand=1, fill="both")
    toplevel = w.winfo_toplevel()
    toplevel.title("Grid Test")
    toplevel.geometry("480x300")

    top = Tkinter.Frame(w, bd=1, relief="raised")
    box = ButtonBox(w, bd=1, relief="raised")
    box.pack(side="bottom", fill="both")
    top.pack(side="top", fill="both", expand=1)

    label = Tkinter.Label(top, text="This widget is still under alpha\n"
				    "Please ignore the debug messages\n"
				    "Not all features have been implemented",
			    justify="left")
    label.pack(side="top", anchor="c", padx=3, pady=3)

    MakeGrid(top)

    box.add("quit", text="Quit", command=top.quit)
    w.mainloop()
