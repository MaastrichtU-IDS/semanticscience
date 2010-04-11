# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2009 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: copyright 26655 2009-01-07 22:02:30Z gregc $

def simpson(f, a, b, n = 2):
	"""Approximate the definite integral of f from a to b
	   by Composite Simpson's rule, dividing the interval in n parts.

	   cribbed from numerical integration wikipedia page
	"""
	assert n > 0
	# forces n to be even
	n = n + (n % 2)
	dx  = (b - a) / float(n)
	ans = f(a) + f(b)
	x = a + dx
	m = 4
	for i in xrange(1, n):
		ans += m * f(x)
		m = 6 - m
		x = x + dx

	return dx * ans / 3


