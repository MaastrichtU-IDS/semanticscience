import base

def registerStandardTools():
	import chimera
	if chimera.nogui:
		return
	m = base.manager
	m.registerExtension(MidasEmulatorEMO(__file__))
	m.registerExtension(SideViewEMO(__file__))
	m.registerExtension(PseudobondPanelEMO(__file__))
	m.registerExtension(TaskPanelEMO(__file__))
	import StructMeasure.gui
	for name in StructMeasure.gui.pageNames:
		m.registerExtension(StructMeasureEMO(__file__, name))

	m.registerExtension(CameraEMO(__file__))
	m.registerExtension(ColorEMO(__file__))
	m.registerExtension(EffectsEMO(__file__))
	m.registerExtension(ReplyLogEMO(__file__))
	m.registerExtension(RotationEMO(__file__))
	#m.registerExtension(TextureEMO(__file__))

	# selection inspector not needed as explicit tool;
	# available from Actions...Inspect and from button
	# at lower right of Chimera main window
	#m.registerExtension(SelectionInspectorEMO(__file__))

StdFavorites = {
	base.makeExtensionKey("Model Panel")	: 0,
	base.makeExtensionKey("Side View")	: 1,
	base.makeExtensionKey("Command Line")	: 2,
	base.makeExtensionKey("Sequence")	: 3,
	base.makeExtensionKey("Reply Log")	: 4,
}

#
# Extension management objects for standard tools
#

MidasEmulator = "Command Line"
meInst = None

class MidasEmulatorEMO(base.EMO):
	def name(self):
		return MidasEmulator
	def description(self):
		return "Display command line interface"
	def categories(self):
		return [ "General Controls" ]
	def icon(self):
		import Midas
		return getModuleImage(Midas, "midas.png")
	def activate(self):
		global meInst
		if not meInst:
			meInst = _MidasInstance()
		meInst.emRaise()

class _MidasInstance:
	def __init__(self):
		base.manager.registerInstance(self)
	def emName(self):
		return MidasEmulator
	def emRaise(self):
		from Midas import midas_ui
		midas_ui.createUI()
	def emHide(self):
		from Midas import midas_ui
		midas_ui.hideUI()
	def emQuit(self):
		self.emHide()
		base.manager.deregisterInstance(self)
		global meInst
		meInst = None

class SideViewEMO(base.EMO):
	def name(self):
		return "Side View"
	def description(self):
		return "Manipulate clipping planes and scaling"
	def categories(self):
		return [ "Viewing Controls" ]
	def icon(self):
		import chimera
		import os.path
		file = chimera.pathFinder().firstExistingFile("chimera",
					os.path.join("images", "sideview.png"),
					False, False)
		if not file:
			return None
		return file
	def activate(self):
		raiseViewingTab("SideView")

class PseudobondPanelEMO(base.EMO):
	def name(self):
		return "PseudoBond Panel"
	def description(self):
		return "Manipulate current pseudobond groups"
	def categories(self):
		return [ "General Controls" ]
	def activate(self):
		from chimera import dialogs, pbgPanel
		dialogs.display(pbgPanel.PseudoBondGroupPanel.name)

class TaskPanelEMO(base.EMO):
	def name(self):
		return "Task Panel"
	def description(self):
		return "Manage foreground and background tasks"
	def categories(self):
		return [ "General Controls" ]
	def activate(self):
		from chimera import dialogs, tasks
		dialogs.display(tasks.TaskPanel.name)

class StructMeasureEMO(base.EMO):
	def __init__(self, path, name):
		self._name = name
		base.EMO.__init__(self, path)
	def name(self):
		return self._name
	def description(self):
		return "Structure measurement: %s" % self._name
	def categories(self):
		if self.name() == "Adjust Torsions":
			return [ "Structure Editing" ]
		return [ "Structure Analysis" ]
	def activate(self):
		raiseStructMeasureTab(self.name())

class CameraEMO(base.EMO):
	def name(self):
		return "Camera"
	def description(self):
		return "Manipulate viewing parameters"
	def categories(self):
		return [ "Viewing Controls" ]
	def activate(self):
		raiseViewingTab("Camera")

class ColorEMO(base.EMO):
	def name(self):
		return "Color Editor"
	def description(self):
		return "Display color editor"
	def categories(self):
		return [ "Utilities" ]
	def activate(self):
		from chimera import dialogs
		dialogs.display("color editor")

class EffectsEMO(base.EMO):
	def name(self):
		return "Effects"
	def description(self):
		return "Manipulate depth cueing"
	def categories(self):
		return [ "Viewing Controls" ]
	def activate(self):
		raiseViewingTab("Effects")

class ReplyLogEMO(base.EMO):
	def name(self):
		return "Reply Log"
	def description(self):
		return "Display reply log window"
	def categories(self):
		return [ "Utilities" ]
	def activate(self):
		from chimera import dialogs, tkgui
		dialogs.display(tkgui._ReplyDialog.name)

class RotationEMO(base.EMO):
	def name(self):
		return "Rotation"
	def description(self):
		return "Manipulate center of rotation"
	def categories(self):
		return [ "Movement" ]
	def activate(self):
		raiseViewingTab("Rotation")

class TextureEMO(base.EMO):
	def name(self):
		return "2D Texture"
	def description(self):
		return "Display texture editor"
	def categories(self):
		return [ "Utilities" ]
	def activate(self):
		from chimera import dialogs, texture
		dialogs.display(texture.TextureDialog.name)

class SelectionInspectorEMO(base.EMO):
	def name(self):
		return "Selection Inspector"
	def description(self):
		return "Display selection inspector"
	def categories(self):
		return [ "General Controls" ]
	def activate(self):
		from chimera import dialogs, tkgui
		dialogs.display(tkgui._InspectDialog.name)

# Utility functions

def raiseViewingTab(tab):
	from chimera import dialogs, viewing
	d = dialogs.display(viewing.ViewerDialog.name)
	d.nb.raise_page('p' + tab)

def raiseStructMeasureTab(tab):
	from chimera import dialogs
	from StructMeasure.gui import StructMeasure
	d = dialogs.display(StructMeasure.name)
	d.notebook.selectpage(tab)

def getModuleImage(module, imageName):
	import os.path
	return os.path.join(os.path.dirname(module.__file__), imageName)
