# need this file for package importing.
"""Generically useful CGL Tk additions"""

import Tkinter

from AquaTkFixes import balloonDontTakeFocus, raiseWindow

def textForeground(bg, master=None):
	"""Return text foreground color for given background color"""
	if master == None:
		master = Tkinter._default_root
	r, g, b = master.winfo_rgb(bg)
	# From: tk_setPalette code:
	# Note that the range of each value in the triple returned by
	# [winfo rgb] is 0-65535, and your eyes are more sensitive to
	# green than to red, and more to red than to blue.
	if r + 1.5 * g + 0.5 * g > 81983:
		return 'black'
	return 'white'
