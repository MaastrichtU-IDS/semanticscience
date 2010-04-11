# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Ink.py 26655 2009-01-07 22:02:30Z gregc $

import colorsys

# For PIL versions prior to 1.0, you need to use the struct code
# to handle byte ordering problems
#import struct

def RGB(r, g, b, a=1.0):
	nr = int(r * 255)
	ng = int(g * 255)
	nb = int(b * 255)
	na = int(a * 255)
	#return struct.unpack('i', struct.pack('BBBB', nr, ng, nb, na))[0]
	#return na << 24 | nb << 16 | ng << 8 | nr
	return (nr, ng, nb, na)

def RGBgray(r, g, b, a=1.0):
	return 0.299 * r + 0.587 * g + 0.114 * b

def HLS(h, l, s, a=1.0):
	r, g, b = colorsys.hls_to_rgb(h, l, s)
	return RGB(r, g, b, a)

def HLSgray(h, l, s, a=1.0):
	r, g, b = colorsys.hls_to_rgb(h, l, s)
	return RGBgray(r, g, b)

def HSV(h, s, v, a=1.0):
	r, g, b = colorsys.hsv_to_rgb(h, s, v)
	return RGB(r, g, b, a)

def HSVgray(h, s, v, a=1.0):
	r, g, b = colorsys.hsv_to_rgb(h, s, v)
	return RGBgray(r, g, b)

def YIQ(y, i, q, a=1.0):
	r, g, b = colorsys.yiq_to_rgb(y, i, q)
	return RGB(r, g, b, a)

def YIQgray(y, i, q, a=1.0):
	return y

def CMYK(c, m, y, k, a=1.0):
	k1 = 1 - k
	c = c * k1 + k
	m = m * k1 + k
	y = y * k1 + k
	return RGB(1 - c, 1 - m, 1 - y, a)

def CMYKgray(c, m, y, k, a=1.0):
	k1 = 1 - k
	c = c * k1 + k
	m = m * k1 + k
	y = y * k1 + k
	return RGBgray(1 - c, 1 - m, 1 - y)

def Gray(g, a=1.0):
	return RGB(g, g, g, a)
