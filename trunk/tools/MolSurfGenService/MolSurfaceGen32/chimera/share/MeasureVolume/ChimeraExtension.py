import chimera.extension

# -----------------------------------------------------------------------------
#
class Surface_Volume_EMO(chimera.extension.EMO):

	def name(self):
		return 'Measure Volume and Area'
	def description(self):
		return 'Compute volume enclosed by a surface and surface area.'
	def categories(self):
		return ['Volume Data', 'Surface/Binding Analysis']
	def icon(self):
		return None
#		return self.path('gumball.png')
	def activate(self):
		self.module('gui').show_surface_volume_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Surface_Volume_EMO(__file__))


# -----------------------------------------------------------------------------
#
def measure_area():
	from MeasureVolume import report_selected_areas
	report_selected_areas()
def measure_volume():
	from MeasureVolume import report_selected_volumes
	report_selected_volumes()
from Accelerators import add_accelerator
add_accelerator('ma', 'Measure area of selected surfaces', measure_area)
add_accelerator('mv', 'Measure volume of selected surfaces', measure_volume)
