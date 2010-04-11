# Copyright (c) 2009 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: version.py.in 29047 2009-10-14 21:11:40Z gregc $

def compare(r0, r1):
	# compare two release number lists, e.g., [1, 3, 2600]
	if len(r0) < len(r1):
		diff = len(r1) - len(r0)
		r0 = r0[:-1] + diff * [0] + r0[-1:]
	elif len(r1) < len(r0):
		diff = len(r0) - len(r1)
		r1 = r1[:-1] + diff * [0] + r1[-1:]
	return cmp(r0, r1)

def newer(r0, r1):
	return compare(r0, r1) > 0

def sameVersion(r0, r1):
	# check two release number lists, but ignore build numbers
	if len(r0) < len(r1):
		diff = len(r1) - len(r0) - 1
		r0 = r0[:-1] + diff * [0]
		r1 = r1[:-1]
	elif len(r1) < len(r0):
		diff = len(r0) - len(r1) - 1
		r1 = r1[:-1] + diff * [0]
		r0 = r0[:-1]
	else:
		r0 = r0[:-1]
		r1 = r1[:-1]
	return r0 == r1

def expandVersion(ver):
	ver = ver.replace('_b', '.')
	return [int(i) for i in ver.split('.')]

def buildVersion(nums):
	return '%s (build %s)' % ('.'.join(str(i) for i in nums[:-1]), nums[-1])

release = "1.5_b29795"		# change major.minor[.bugfix] part by hand
releaseNum = expandVersion(release)
version = "alpha version %s (build %s) 2010-01-15 21:36:19 GMT" \
						% tuple(release.rsplit('_b'))

if __name__ == "__main__":
	print "version:", version
	print "build version:", buildVersion(releaseNum)
