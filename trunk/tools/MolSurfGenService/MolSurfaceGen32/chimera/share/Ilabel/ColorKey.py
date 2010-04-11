# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ColorKey.py 29408 2009-11-23 19:54:11Z gregc $

import chimera

from PythonModel.PythonModel import PythonModel
class KeyModel(PythonModel):
	def __init__(self, gui):
		PythonModel.__init__(self)
		self.gui = gui
		chimera.openModels.add([self], baseId=-1, hidden=True)

	def destroy(self, *args):
		PythonModel.destroy(self, True)

	def computeBounds(self, sphere, bbox):
		return False

	def validXform(self):
		return False

	def draw(self, lens, viewer, passType):
		if passType != chimera.LensViewer.Overlay2d:
			return
		self._draw("opengl", viewer)

	def _draw(self, mode, viewer):
		gui = self.gui
		if not gui.keyPosition or len(gui.keyPosition) < 2:
			return

		w, h = viewer.windowSize

		openGL = mode == "opengl"
		if openGL:
			from OpenGL import GL
		else:
			# X3D mostly cribbed from ILabelModel's x3dWrite
			prefix = self.x3dPrefix
			output = self.x3dOutput
			FONTDEF = "<FontStyle DEF='ColorKey' family='%s' size='%s' style='%s'>\n"
			ENDFONTDEF = "</FontStyle>\n"
			FONTUSE = "<FontStyle USE='ColorKey'/>\n"
			FILENAME = "<MetadataString value='\"%s\"' name='filename'/>\n"
			TEXT = "<Text string='%s'>\n"
			ENDTEXT = "</Text>\n"
			TRANS = "<Transform translation='%g %g %g'>\n"
			TRANSCALE = "<Transform translation='%g %g %g' scale='%g %g %g'>\n"
			ENDTRANS = "</Transform>\n"
			SHAPE = "<Shape>\n"
			ENDSHAPE = "</Shape>\n"
			APPEAR = "<Appearance>\n"
			ENDAPPEAR = "</Appearance>\n"
			MAT = "<Material ambientIntensity='0' diffuseColor='0 0 0' shininess='0' emissiveColor='%g %g %g'/>\n"
			MATTRANS = "<Material ambientIntensity='0' diffuseColor='0 0 0' shininess='0' emissiveColor='%g %g %g' transparency='%g'/>\n"
			OVERLAY = "<MetadataString value='\"2D overlay\"' name='model type'/>\n"
			# translate to hither plane and scale to match pixels
			cam = viewer.camera
			view = 0
			eyePos = cam.eyePos(view)
			left, right, bottom, top, hither, yon, focal = \
							cam.window(view)
			scale = (right - left) / w
			xlate_scale = (eyePos[0] + left, eyePos[1] + bottom,
					eyePos[2] - hither, scale, scale, 1)
			output.extend([ prefix, OVERLAY,
					prefix, TRANSCALE % xlate_scale ])
		x1, x2 = w * gui.keyPosition[0][0], w * gui.keyPosition[1][0]
		y1, y2 = h * gui.keyPosition[0][1], h * gui.keyPosition[1][1]
		minX, maxX = min(x1, x2), max(x1, x2)
		minY, maxY = min(y1, y2), max(y1, y2)
		if maxX - minX > maxY - minY:
			layout = "horizontal"
			shortMin, shortMax = minY, maxY
			longMin, longMax = minX, maxX
		else:
			layout = "vertical"
			shortMin, shortMax = minX, maxX
			longMin, longMax = minY, maxY
		colorTreatment = gui.colorTreatment.get()
		if colorTreatment == "blended":
			rectSize = (longMax-longMin) / (len(gui.wells)-1)
			rectPositions = [ longMin + i * rectSize
					for i in range(len(gui.wells)) ]
			if layout == "vertical":
				rectPositions.reverse()
			labelPositions = rectPositions
		else:
			rectSize = (longMax-longMin) / len(gui.wells)
			rectPositions = [ longMin + i * rectSize
					for i in range(len(gui.wells)+1) ]
			if layout == "vertical":
				rectPositions.reverse()
			labelPositions = [
				(rectPositions[i] + rectPositions[i+1]) / 2
					for i in range(len(rectPositions)-1)]

		if openGL:
			GL.glPushMatrix()
		borderColor = gui.borderColor.get()
		if borderColor != None:
			bd = gui.borderWidth.get()
			# increase linewidth when printing
			bd *= chimera.LODControl.get().fontAdjust()
			# for raytracing, needs to be slightly behind key
			self._layoutRect(openGL, layout,
					shortMin-bd, shortMax+bd,
					longMin-bd, longMax+bd,
					borderColor, borderColor, z=-0.001)
		else:
			bd = 0
		labelColor = gui.labelColor.get()
		for i in range(len(rectPositions) - 1):
			color1 = gui.wells[i].rgba
			if len(rectPositions) == len(gui.wells):
				color2 = gui.wells[i+1].rgba
			else:
				color2 = color1
			self._layoutRect(openGL, layout, shortMin, shortMax,
				rectPositions[i], rectPositions[i+1],
				color1, color2)
		if gui.tickMarks.get():
			tickSize = 10
			tickSize *= chimera.LODControl.get().fontAdjust()
			tickThickness = 4
			tickThickness *= chimera.LODControl.get().fontAdjust()
		else:
			tickSize = 0
		side = gui.labelPos.get()
		if (side == "right/bottom" and layout == "vertical") or (side
				== "left/top" and layout == "horizontal"):
			keyEdge = shortMax + bd
			tickTip = keyEdge + tickSize
			labelOffset = 5
		else:
			keyEdge = shortMin - bd
			tickTip = keyEdge - tickSize
			labelOffset = -5
		labelInfo = []
		for i, lp in enumerate(labelPositions):
			corr = 0
			if gui.tickMarks.get():
				if colorTreatment == "blended":
					if lp == labelPositions[0]:
						corr = max(0,
							tickThickness/2 - bd)
						if layout == "vertical":
							corr = -corr
					elif lp == labelPositions[-1]:
						corr = max(0,
							tickThickness/2 - bd)
						if layout == "horizontal":
							corr = -corr
				if bd == 0:
					color = gui.wells[i].rgba
				else:
					color = borderColor
				self._layoutRect(openGL, layout, keyEdge,
					tickTip, lp-tickThickness/2+corr,
					lp+tickThickness/2+corr, color, color)
			text = gui.labels[i].variable.get()
			if layout == "vertical":
				lx = tickTip + labelOffset
				ly = lp + corr
			else:
				lx = lp + corr
				ly = tickTip + labelOffset
			rgba = gui.labelColor.get()
			if rgba == None:
				rgba = gui.wells[i].rgba
			labelInfo.append((lx, ly, text, rgba))
		font = chimera.OGLFont(gui.keyFontTypeface.get(),
				gui.keyFontSize.get(), gui.keyFontStyle.get())
		font.setup()
		# determine justification offsets
		if layout == "vertical":
			widths = []
			fieldWidth = 0
			justification = gui.justification.get()
			for x, y, text, rgba in labelInfo:
				if side == "right/bottom":
					if justification == "decimal point":
						try:
							dp = text.rindex('.')
						except ValueError:
							dp = len(text)
						width = font.width(text[:dp])
					elif justification == "right":
						width = font.width(text)
					else:
						width = 0
				else:
					if justification == "decimal point":
						try:
							dp = text.rindex('.')
						except ValueError:
							dp = -1
						width = font.width(text[dp+1:])
					elif justification == "left":
						width = font.width(text)
					else:
						width = 0
				widths.append(width)
				fieldWidth = max(fieldWidth, width)
			justifyOffsets = [(fieldWidth - w) for w in widths]
		else:
			justifyOffsets = [0] * len(labelInfo)
			pushDown = max([font.height(info[2])[0] for info in labelInfo])
		if not openGL:
			firstFont = True
		labelOffset = gui.labelOffset.get()
		for li, jo in zip(labelInfo, justifyOffsets):
			x, y, text, rgba = li
			if not text:
				continue
			if layout == "vertical":
				y -= font.height(text)[0] / 2
				if side == "left/top":
					x -= font.width(text) + jo + labelOffset
				else:
					x += jo + labelOffset
			else:
				import sys
				x -= font.width(text) / 2
				if side == "right/bottom":
					y -= pushDown + labelOffset
				else:
					y += labelOffset
			if openGL:
				GL.glPushMatrix()
				GL.glTranslatef(x, y, 0.0)
				font.setColor(*rgba)
				font.draw(text)
				GL.glPopMatrix()
			else:
				output.extend([prefix, ' ', TRANS % (x, y, 0)])
				output.extend([prefix, '  ', SHAPE])
				output.extend([prefix, '   ', APPEAR])
				if rgba[3] != 1:
					rgbt = rgba[0:3] + (1 - rgba[3],)
					output.extend([prefix, '   ',
							MATTRANS % rgbt])
				else:
					output.extend([prefix, '   ',
							MAT % rgba[0:3]])
				output.extend([prefix, '   ', ENDAPPEAR])
				output.extend([prefix, '   ',
						TEXT % chimera.xml_quote(text)])
				if firstFont:
					output.extend([prefix, '    ',
						FONTDEF % (font.x3dFamily(),
						font.size(), font.x3dStyle()),
						prefix, '     ',
						FILENAME % font.filename(),
						prefix, '    ', ENDFONTDEF])
				else:
					output.extend([prefix, '    ',
								FONTUSE])
				output.extend([prefix, '   ', ENDTEXT])
				output.extend([prefix, '  ', ENDSHAPE])
				output.extend([prefix, ' ', ENDTRANS])
				firstFont = False
		font.cleanup()
		if openGL:
			GL.glPopMatrix()
		else:
			output.extend([prefix, ENDTRANS])

	def x3dNeeds(self, scene):
		gui = self.gui
		if not gui.keyPosition or len(gui.keyPosition) < 2:
			return

		# for FontStyle, Text
		scene.needComponent(chimera.X3DScene.Text, 1)
		# for TriangleStripSet
		#scene.needComponent(chimera.X3DScene.Rendering, 3)
		# for ColorRGBA
		scene.needComponent(chimera.X3DScene.Rendering, 4)

	def x3dWrite(self, indent, scene):
		gui = self.gui
		if not gui.keyPosition or len(gui.keyPosition) < 2:
			return

		self.x3dPrefix = " " * indent
		self.x3dOutput = []
		self._draw("x3d", chimera.viewer)
		return ''.join(self.x3dOutput)

	def _layoutLine(self, layout, fixedMin, fixedMax, var, color):
		if layout == "vertical":
			x1, x2, y1, y2 = fixedMin, fixedMax, var, var
		else:
			x1, x2, y1, y2 = var, var, fixedMin, fixedMax
		
		from OpenGL import GL
		GL.glColor4f(*tuple(color))
		GL.glBegin(GL.GL_LINES)
		GL.glVertex2f(x1, y1)
		GL.glVertex2f(x2, y2)
		GL.glEnd()

	def _layoutRect(self, openGL, layout, fixedMin, fixedMax,
					varMin, varMax, color1, color2, z=0):
		if layout == "vertical":
			x1, x2, y1, y2 = fixedMin, fixedMax, varMin, varMax
			colors = [color1, color1, color2, color2]
		else:
			x1, x2, y1, y2 = varMin, varMax, fixedMin, fixedMax
			colors = [color1, color2, color2, color1]
		
		if openGL:
			from OpenGL import GL
			GL.glBegin(GL.GL_QUADS)
			GL.glColor4f(*tuple(colors[0]))
			GL.glVertex2f(x1, y1)
			GL.glColor4f(*tuple(colors[1]))
			GL.glVertex2f(x2, y1)
			GL.glColor4f(*tuple(colors[2]))
			GL.glVertex2f(x2, y2)
			GL.glColor4f(*tuple(colors[3]))
			GL.glVertex2f(x1, y2)
			GL.glEnd()
			# to sidestep backface culling, draw another quad
			# in the other order
			GL.glBegin(GL.GL_QUADS)
			GL.glColor4f(*tuple(colors[3]))
			GL.glVertex2f(x1, y2)
			GL.glColor4f(*tuple(colors[2]))
			GL.glVertex2f(x2, y2)
			GL.glColor4f(*tuple(colors[1]))
			GL.glVertex2f(x2, y1)
			GL.glColor4f(*tuple(colors[0]))
			GL.glVertex2f(x1, y1)
			GL.glEnd()
		else:
			output = self.x3dOutput
			prefix = self.x3dPrefix
			SHAPE = "<Shape>\n"
			ENDSHAPE = "</Shape>\n"
			APPEAR = "<Appearance>\n"
			ENDAPPEAR = "</Appearance>\n"
			TRIANGLESTRIP = "<TriangleStripSet solid='false' stripCount='4'>\n"
			ENDTRIANGLESTRIP = "</TriangleStripSet>\n"
			COLOR = "<ColorRGBA color='"
			ENDCOLOR = "'/>\n"
			COORD = "<Coordinate point='"
			ENDCOORD = "'/>\n"
			MAT = "<Material ambientIntensity='0' diffuseColor='0 0 0' shininess='0'/>\n"
			output.extend([
				prefix, ' ', SHAPE,
				prefix, '  ', APPEAR,
				prefix, '   ', MAT,
				prefix, '  ', ENDAPPEAR])
			output.extend([prefix, '   ', TRIANGLESTRIP])
			output.extend([prefix, '    ', COLOR])
			for color in [colors[0], colors[1], colors[3],
								colors[2]]:
				output.extend(["%g " % c for c in color])
			output.extend([prefix, '    ', ENDCOLOR])
			output.extend([prefix, '    ', COORD])
			output.extend(["%g " % c for c in [x1, y1, z, x2, y1, z,
							x1, y2, z, x2, y2, z]])
			output.extend([prefix, '    ', ENDCOORD])
			output.extend([prefix, '   ', ENDTRIANGLESTRIP])
			output.extend([prefix, ' ', ENDSHAPE])


	def _layoutTriangle(self, layout, fixedMin, fixedMax, varMin, varMax,
								color):
		if layout == "vertical":
			xs = [fixedMin, fixedMax, fixedMin]
			ys = [varMin, (varMin+varMax)/2.0, varMax]
		else:
			xs = [varMin, (varMin+varMax)/2.0, varMax]
			ys = [fixedMin, fixedMax, fixedMin]
		
		from OpenGL import GL
		GL.glColor4f(*tuple(color))
		GL.glBegin(GL.GL_TRIANGLES)
		for x, y in zip(xs, ys):
			GL.glVertex2f(x, y)
		GL.glEnd()
		# to sidestep backface culling, draw another quad in the other
		# order
		xs.reverse()
		ys.reverse()
		GL.glBegin(GL.GL_TRIANGLES)
		for x, y in zip(xs, ys):
			GL.glVertex2f(x, y)
		GL.glEnd()
