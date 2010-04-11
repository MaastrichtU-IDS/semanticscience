# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: chimage.py 28845 2009-09-23 17:36:34Z gregc $

import chimera
from PIL import Image, ImageTk
import Tkinter
Tk = Tkinter

# "preinit"ialize the imaging library and add any other formats that we expect
Image.preinit()
# Png now preloaded as part of Imaging 1.1.2
#from PIL import PngImagePlugin

def get(image, master, allowRelativePath=False):
	"""Get image from standard locations.

	get(image, master) => TkImage

	image can be either a filename (or URL) or a Image.Image.  Filenames
	are searched for by chimera.pathFinder().  Master is the widget the
	result TkImage will be created for.  The master is needed for the Tk
	interpreter to place the image in and to find out the background color
	to blend the image with if it is semi-transparent.
	"""

	if isinstance(image, basestring):
		import os.path
		if allowRelativePath or os.path.isabs(image):
			filename = image
		else:
			filename = chimera.pathFinder().firstExistingFile(
						"chimera",
						os.path.join("images", image),
						False, False)
			if not filename:
				import errno
				raise IOError(errno.ENOENT,
					os.strerror(errno.ENOENT), image)
		try:
			image = Image.open(filename)
		except IOError, e:
			# PIL's IOError is missing the filename
			e = IOError(*(e.args + (filename,)))
			raise e
	elif isinstance(image, ImageTk.PhotoImage) \
	  or isinstance(image, ImageTk.BitmapImage):
		return image
	elif not isinstance(image, Image.Image):
		raise TypeError, "image must be filename or Image"

	if master == None:
		master = Tk._default_root

	r, g, b = master.winfo_rgb(master["background"])
	rgb = r / 255, g / 255, b / 255
	if image.mode == "1":
		imtk = ImageTk.BitmapImage(image, master=master)
	elif image.mode == "P" and image.info.has_key("transparency"):
		# palette + transparency property (GIF, PNG, XPM).
		# create a transparency mask, and paste the image
		# onto a solid background through that mask.
		lut = [255] * 256
		lut[image.info["transparency"]] = 0
		i = Image.new("RGB", image.size, rgb)
		i.paste(image, None, image.point(lut, "1"))
		imtk = ImageTk.PhotoImage(i, master=master)
	elif image.mode == "RGBA":
		# true color with transparency (PNG, TIFF).  Simpily
		# paste it onto a background image
		i = Image.new("RGB", image.size, rgb)
		i.paste(image, None, image)
		imtk = ImageTk.PhotoImage(i, master=master)
	else:
		imtk = ImageTk.PhotoImage(image, master=master)
	return imtk
