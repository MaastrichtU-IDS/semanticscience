import re
import Tkinter
Tk = Tkinter

import chimera
from chimera import replyobj

root = None
_reply = None
splash = None

def _earlyExit():
	raise SystemExit(1)

_extraArgs = []
def _openDocument(*pathnames):
	global _extraArgs
	_extraArgs.extend(pathnames)

def create():
	global root
	global _reply
	global splash
	root = Tk.Tk(screenName=chimera.screen, className=chimera.AppName,
							sync=chimera.debug)
	splash = Tk.Frame(root, background="white")
	splash.columnconfigure(0, weight=1)
	splash.columnconfigure(2, weight=1)
	splash.rowconfigure(0, weight=1)
	root.title(chimera.title)
	if chimera.geometry:
		root.geometry(chimera.geometry)
	splash.master.protocol("WM_DELETE_WINDOW", _earlyExit)

	status = Tk.Label(splash, background="white", foreground="black",
			font="Helvetica -14 italic", anchor=Tk.W,
			justify=Tk.LEFT, borderwidth=0, text='startup status')
	status.grid(row=1, column=0, columnspan=2, sticky=Tk.EW)

	import chimage
	icon = chimage.get('chimera48.png', splash)
	logo = Tk.Label(splash, image=icon, borderwidth=0)
	logo.__image = icon
	logo.grid(row=0, column=0, sticky=Tk.E)

	icon = chimage.get('titleChimera.png', root)
	title = Tk.Label(splash, image=icon, borderwidth=0)
	title.__image = icon
	title.grid(row=0, column=1, sticky=Tk.EW)

	icon2 = chimage.get('brand.png', root)
	brand = Tk.Label(splash, image=icon2, borderwidth=0)
	brand.__image = icon2
	brand.grid(row=0, rowspan=2, column=2, sticky=Tk.W)

	winsys = splash.tk.call('tk', 'windowingsystem')
	if winsys == 'win32':
		import os.path
		filename = chimera.pathFinder().firstExistingFile("chimera",
					os.path.join("Icons", "chimera32.ico"),
					False, False)
		if filename:
			# this requires Tcl/Tk 8.3.3 (or newer)
			# top.wm_iconbitmap(filename)
			root.tk.call('wm', 'iconbitmap', root._w, filename)
	elif winsys == 'aqua':
		# in Tk 8.5 (8.6 carbon?), need to set useCustomMDEF for
		# images and colors in menus entries
		splash.tk.call("set", "::tk::mac::useCustomMDEF", "1")
		splash.tk.createcommand('::tk::mac::OpenDocument',
								_openDocument)

	splashReply = replyobj.SplashReply(status)
	_reply = replyobj.pushReply(splashReply, takeStdout=0, takeStderr=0)

	splash.pack(expand=True, fill=Tk.BOTH)
	if not splash.winfo_viewable():
		splash.wait_visibility()

def interpreter():
	return root.tk.interpaddr()

def destroy():
	global splash
	global _reply
	splash.destroy()
	splash = None
	replyobj.popReply(_reply)
	_reply = None
	return _extraArgs
