#!/usr/local/bin/python
# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: gprof.py 26655 2009-01-07 22:02:30Z gregc $

import string
from pstats import Stats

def func_alt_string(func_name):
	file, line, name = func_name
	return '%s(%s:%d)' % (name, file, line)
def find_width(dict):
	width = 0
	for k in dict.keys():
		w = len(func_alt_string(k))
		if w > width:
			width = w
	return width

class Gprof(Stats):
	def __init__(self, *args):
		apply(Stats.__init__, (self,) + args)
	def print_callees(self, *amount):
		width, list = self.get_print_list(amount)
		if list:
			self.calc_callees()

			self.print_call_heading(width, "called...")
			for func in list:
				if self.all_callees.has_key(func):
					self.gprint_call_line(width, \
						  func, self.all_callees[func])
				else:
					self.gprint_call_line(width, func, {})
			print
			print
		return self
	def gprint_call_line(self, name_size, source, call_dict):
		t = self.stats[source]
		if t[3] == 0:
			percent = 0
		else:
			percent = t[2] / t[3] * 100
		print string.ljust(func_alt_string(source), name_size) \
			+ '%f (%d, %f, %.1f%%)' % (t[3], t[0], t[2], percent)

		clist = call_dict.keys()
		clist.sort()
		name_size = name_size + 2
		for func in clist:
			name = func_alt_string(func)
			ft = self.stats[func]
			tm = call_dict[func] / float(ft[0]) * ft[3]
			if t[3] == 0:
				percent = 0
			else:
				percent = tm / t[3] * 100
			print ' '*name_size + name + ' (%d, %f, %.1f%%)' \
				  % (call_dict[func], tm, percent)

if __name__ == '__main__':
	gp = Gprof('z')
	gp.strip_dirs().print_callees()
