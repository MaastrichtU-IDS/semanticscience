"""Access to Chimera OpenGL drawing from Python"""

import _pm
import chimera

class PythonModel(_pm._PythonModel):
	"""OpenGL drawing from Python

	   This interface may change from release to release.  If you have
	   difficulties using PythonModel, send any questions you have to
	   chimera-dev@cgl.ucsf.edu
	"""

	def close(self):
		_pm._PythonModel.close(self, 1)

	# Below are callback routines invoked from the C++ layer

	def draw(self, lens, viewer, drawPass):
		pass

	def drawPick(self, lens, viewer):
		pass

	def invalidateCache(self, lens):
		pass

	def invalidateSelection(self, lens):
		pass

	def computeBounds(self, sphere, bbox):
		return False

	def validXform(self):
		return True

	def mass(self, lens):
		"""Return mass of model"""
		return 0

	def cofm(self, lens):
		"""Return "center of mass" of model"""
		return chimera.Point(0, 0, 0)

	def x3dNeeds(self, scene):
		"""Give X3D component levels needed to display X3D content"""
		pass

	def x3dWrite(self, indent, lens):
		"""Return string containing model in X3D"""
		return ""

chimera.triggers.addTrigger('PythonModel')
