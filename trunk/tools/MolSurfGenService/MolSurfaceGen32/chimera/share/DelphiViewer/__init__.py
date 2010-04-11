# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""View Delphi output in Chimera

File:		__init__.py
Date:		06.08.2000
Description:	Handles the logic and GUI interface for setting up a DelPhi.

Imports:	- DelPhiInputGUI
		- DelPhiExecutor

Classes:	DelPhiController
	Input:	- Various parameter for a DelPhi run.  Listed in DelPhi
		manual.  A lot of parameters!
		- Either input files or defaults for charge and radius
		files.
		- Either input files or chimera models.
	Output:	- eps, phi or srf files corresponding to
		atomic electrostatic potential data, grid electrostatic
		potential data or GRASP surfaces files, respectively.

Caveats:

Last modified:	06.12.2000 - Added header and print statements.
                12.14.2006 - Updated to use newer GUI interface
"""

# general modules
import os
import Tkinter

# delphi/chimera-related modules
import chimera
from chimera import replyobj
import DelPhiInputGUI
import DelPhiExecutor
import DelPhiOutputGUI

controller = None

def run():
	global controller
	if controller is None:
		controller = DelPhiController()
	else:
		controller.gui.enter()

class DelPhiController:

	def __init__(self):
		#print self, "Initializing..."
		self.checkHandler = None
		self.InputGUI()
		#print self, "Done initializing."

	def __del__(self):
		if self.checkHandler:
			chimera.triggers.deleteHandler("check for changes",
							self.checkHandler)

	def InputGUI(self):
		#print self, "Running input GUI..."
		self.gui = DelPhiInputGUI.DelPhiInputGUI(self.Execute,
								self.Abort)
		#print self, "Done running input GUI."

	def Execute(self, options):
		#print self, "Executing DelPhi..."
		self.options = options
		self.executor = DelPhiExecutor.DelPhiExecutor(self.options)
		self.process = self.executor()		
		self.checkHandler = chimera.triggers.addHandler(
						"check for changes",
						self.CheckProcess, None)
		replyobj.status("Running DelPhi in background")

	def CheckProcess(self, triggerName, data, data2):
		if not self.process.isRunning():
			chimera.triggers.deleteHandler("check for changes",
						self.checkHandler)
			self.checkHandler = None
			if self.executor.success():
				#print self, "Done executing DelPhi."
				self.OutputGUI()
				self.gui.savePrefs()
				replyobj.status("DelPhi finished")
			else:
				replyobj.status("DelPhi failed")

	def OutputGUI(self):
		#print self, "Running output GUI..."
		DelPhiOutputGUI.DelPhiOutputGUI(self.options)
		#print self, "Done running output GUI."

	def Abort(self, options):
		#print self, "User requested abort..."
		#print self, "Aborting."
		pass
	
if __name__ == '__main__':
	import sys
	import Tkinter
	root = Tkinter.Tk()
	dpc = DelPhiController(None)
	dpc()
	root.mainloop()
