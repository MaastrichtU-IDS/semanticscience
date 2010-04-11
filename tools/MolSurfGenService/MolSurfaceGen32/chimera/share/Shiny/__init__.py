def display():
	import Lighting
	controller = Lighting.get()
	from chimera.extension.StdTools import raiseViewingTab
	raiseViewingTab(controller.Name)
	controller.showInterface(controller.Interface_Shininess)
