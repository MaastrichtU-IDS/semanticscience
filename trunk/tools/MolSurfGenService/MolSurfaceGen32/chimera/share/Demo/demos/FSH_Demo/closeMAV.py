import chimera

def findMAVs():
	# locate and return running instances of MultAlign Viewer
	from MultAlignViewer.MAViewer import MAViewer
	from chimera.extension import manager
	mavs = [inst for inst in manager.instances
					if isinstance(inst, MAViewer)]
	return mavs

for mav in findMAVs():
	mav.Quit()

