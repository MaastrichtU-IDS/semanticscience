import chimera.extension

# -----------------------------------------------------------------------------
#
class Volume_Eraser_EMO(chimera.extension.EMO):

	def name(self):
		return 'Volume Eraser'
	def description(self):
		return 'Erase volume data within a sphere'
	def categories(self):
		return ['Volume Data']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_volume_eraser_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Volume_Eraser_EMO(__file__))

# -----------------------------------------------------------------------------
#
def erase_box_cb():
	import VolumeEraser
	VolumeEraser.zero_volume_inside_selection_box()
def zero_boundary_cb(step = 1):
	import VolumeEraser
	VolumeEraser.zero_volume_boundary(step)
	
# -----------------------------------------------------------------------------
#
from Accelerators import add_accelerator
add_accelerator('eb', 'Erase volume data inside subregion selection box',
		erase_box_cb)
add_accelerator('zb', 'Zero volume data boundary', zero_boundary_cb)
add_accelerator('zB2', 'Zero volume data boundary for step size 2',
		lambda zb=zero_boundary_cb: zb(2))
add_accelerator('zB4', 'Zero volume data boundary for step size 4',
		lambda zb=zero_boundary_cb: zb(4))
