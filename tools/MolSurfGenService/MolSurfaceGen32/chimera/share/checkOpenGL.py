# This script is for checking if there are any problems in the OpenGL
# configuration.

# sys.argv[1] is the platform (`uname -s` output), but we only do this on
# Linux, so ignore it for now.

import sys, os

libGL = ('/usr/lib/libGL.so.1', '/usr/X11R6/lib/libGL.so.1')

def ignoreMisconfiguration():
	import Tkinter, tkMessageBox as mb
	tk = Tkinter.Tk()
	tk.withdraw()
	#winsys = tk.tk.call('tk', 'windowingsystem')
	#if winsys == 'win32':
	#	filename = os.path.join(os.path.dirname(__file__), 'chimera',
	#			'Icons', 'chimera32.ico')
	#	tk.wm_iconbitmap(filename)
	message = mb.Message(title="OpenGL miconfiguration",
			icon=mb.ERROR, type=mb.YESNO, default='no',
			message="OpenGL misconfiguration detected.\n"
			"%s differs from %s.\n"
			"\n"
			"See %s installation notes for details at\n"
			"http://www.cgl.ucsf.edu/chimera/download.html.\n"
			"\n"
			"Continue even though chimera might crash?" % (libGL + (sys.argv[1],)))
	return message.show() == 'yes'

if sys.argv[1] == 'Linux':
	# if two different versions of libGL exist, then complain
	try:
		same = os.path.samefile(*libGL)
	except OSError:
		# probably a missing file, which is good
		same = True
	if not same and not ignoreMisconfiguration():
		raise SystemExit, 1

raise SystemExit, 0
