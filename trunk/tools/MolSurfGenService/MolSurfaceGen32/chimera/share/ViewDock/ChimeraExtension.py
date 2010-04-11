# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class ViewDockEMO(chimera.extension.EMO):
	def name(self):
		return 'ViewDock'
	def description(self):
		return 'display and manage dock results'
	def categories(self):
		return ['Surface/Binding Analysis']
	def icon(self):
		return self.path('viewdock.tiff')
	def activate(self):
		self.module('choose').ViewDockCB()
		# Instance will register itself
		return None
	def cmdViewdock(self, cmdname, args):
		args = args.strip()
		if not args:
			from chimera import UserError
			raise UserError("please specify input file name and type")
		filename, remainder = self.splitArgs(args)
		filters = [ t[0] for t in self.module('choose').Filters ]
		if remainder:
			filetype, remainder = self.splitArgs(remainder)
			if remainder:
				from chimera import UserError
				raise UserError("too many arguments")
		else:
			filetype = "Dock 4, 5 or 6"
		if filetype not in filters:
			from chimera import UserError
			raise UserError("unknown ViewDock file type")
		self.module('base').ViewDock(filename, filetype)
	def splitArgs(self, args):
		if args[0] != '"':
			fields = args.split(None, 1)
			if len(fields) > 1:
				return fields
			else:
				return fields[0], ""
		else:
			for i in range(1, len(args)):
				if args[i] == '"':
					if args[i - 1] == '\\':
						continue
					return args[1:i], args[i+1:].strip()
			from chimera import UserError
			raise UserError("unterminated quoted string")
emo = ViewDockEMO(__file__)
chimera.extension.manager.registerExtension(emo)
from Midas.midas_text import addCommand
addCommand("viewdock", emo.cmdViewdock, help=True)

try:
	import Midi
except ImportError:
	# Nothing out there for sound
	pass
else:
	class HearDockEMO(chimera.extension.EMO):
		def name(self):
			return 'HearDock'
		def description(self):
			return 'display, sonify and manage dock results'
		def categories(self):
			return ['Surface/Binding Analysis']
		def icon(self):
			return self.path('heardock.tiff')
		def activate(self):
			self.module('choose').HearDockCB()
			# Instance will register itself
			return None
	chimera.extension.manager.registerExtension(HearDockEMO(__file__))
