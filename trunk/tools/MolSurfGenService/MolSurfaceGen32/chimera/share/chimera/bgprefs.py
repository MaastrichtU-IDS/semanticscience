# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: bgprefs.py 27425 2009-04-28 22:41:49Z gregc $

"""
background preferences
"""
import chimera
import preferences
import tkoptions

BACKGROUND = "Background"
BG_COLOR = "Background color"
LABEL_FONT = "Label font"
HMETHOD = "Selection highlight method"
HCOLOR = "Selection highlight color"
#LENS_PROFILE = "Draw lens borders"
#LENS_COLOR = "Lens border color"

class HighlightOption(tkoptions.SymbolicEnumOption):
	"""Specialization of SymbolicEnumOption Class for highlights"""
	labels = ("outline", "fill")
	values = [chimera.LensViewer.Outline, chimera.LensViewer.Fill]

def _backgroundColorCB(option):
	rgba = option.get()
	if not rgba:
		color = None
	else:
		color = chimera.MaterialColor(*rgba)
	chimera.viewer.background = color

default_label_font = None
def setLabelFont(option):
	if chimera.nogui:
		return
	name, style, size = option.get()
	if style == 'Bold':
		style = chimera.OGLFont.bold
	elif style == 'Italic':
		style = chimera.OGLFont.italic
	elif style == 'Bold Italic':
		style = chimera.OGLFont.bold | chimera.OGLFont.italic
	else:
		style = chimera.OGLFont.normal
	font = chimera.OGLFont(name, size, style)
	if font.valid():
		global default_label_font
		default_label_font = font
		chimera.OGLFont.setDefaultFont(font)
		chimera.viewer.invalidateCache()

def _highlightMethodCB(option):
	method = option.get()
	chimera.viewer.highlight = method

def _highlightColorCB(option):
	rgba = option.get()
	if not rgba:
		color = None
	else:
		color = chimera.MaterialColor(*rgba)
	chimera.viewer.highlightColor = color

#def _drawBorderCB(option):
#	border = option.get()
#	chimera.viewer.lensBorder = border

#def _borderColorCB(option):
#	rgba = option.get()
#	if not rgba:
#		color = None
#	else:
#		color = chimera.MaterialColor(*rgba)
#	chimera.viewer.lensBorderColor = color

def initialize():
	backgroundPreferences = {
		BG_COLOR: (
			tkoptions.RGBAOption, None, _backgroundColorCB
		),
		LABEL_FONT:
			(tkoptions.FontOption,
				(tkoptions.FontOption.names[0],
				tkoptions.FontOption.styles[0], 16),
				setLabelFont),
	}
	backgroundPreferencesOrder = [ BG_COLOR, LABEL_FONT, ]
	if isinstance(chimera.viewer, chimera.LensViewer):
		backgroundPreferences.update({
			HMETHOD: (
				HighlightOption, chimera.viewer.highlight,
				_highlightMethodCB
			),
			HCOLOR: (
				tkoptions.RGBAOption, chimera.viewer.highlightColor.rgba(),
				_highlightColorCB, { "noneOkay": False }
			),
			#LENS_PROFILE: (
			#	tkoptions.BooleanOption, chimera.viewer.lensBorder,
			#	_drawBorderCB
			#),
			#LENS_COLOR: (
			#	tkoptions.RGBAOption, chimera.viewer.lensBorderColor.rgba(),
			#	_borderColorCB, { "noneOkay": False }
			#)
		})
		backgroundPreferencesOrder.extend([
			HMETHOD, HCOLOR,
		])
	preferences.register(BACKGROUND, backgroundPreferences,
				onDisplay=_bgPrefDisp, onHide=_bgPrefHide)
	preferences.setOrder(BACKGROUND, backgroundPreferencesOrder)

	opt = preferences.getOption(BACKGROUND, LABEL_FONT)
	setLabelFont(opt)

_bgPrefHandler = None

def _bgPrefDisp(event=None):
	global _bgPrefHandler
	if _bgPrefHandler is None:
		_bgPrefHandler = chimera.triggers.addHandler("Viewer",
					_bgPrefUpdate, None)
	_bgPrefUpdate("Viewer", None, None)

def _bgPrefHide(event=None):
	global _bgPrefHandler
	if _bgPrefHandler is not None:
		chimera.triggers.deleteHandler("Viewer", _bgPrefHandler)
		_bgPrefHandler = None

def _bgPrefUpdate(trigger, closure, changed):
	if changed is not None and chimera.viewer not in changed.modified:
		return
	_bgCheckColor(BACKGROUND, BG_COLOR, chimera.viewer.background)
	_bgCheckOpt(BACKGROUND, HMETHOD, chimera.viewer.highlight)
	_bgCheckColor(BACKGROUND, HCOLOR, chimera.viewer.highlightColor)
	#_bgCheckOpt(BACKGROUND, LENS_PROFILE, chimera.viewer.lensBorder)
	#_bgCheckColor(BACKGROUND, LENS_COLOR, chimera.viewer.lensBorderColor)

def _bgCheckColor(cat, opt, c):
	oc = preferences.get(cat, opt)
	if c is None:
		if oc is not None:
			preferences.set(cat, opt, None)
	else:
		nc = c.rgba()
		if oc != nc:
			preferences.set(cat, opt, nc)

def _bgCheckOpt(cat, opt, b):
	ob = preferences.get(cat, opt)
	if ob != b:
		preferences.set(cat, opt, b)
