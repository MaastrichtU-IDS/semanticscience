# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29408 2009-11-23 19:54:11Z gregc $

from OpenGL import GL
from PythonModel.PythonModel import PythonModel
import chimera
from SimpleSession import SAVE_SESSION

import threading
_uidLock = threading.RLock()

from Label import Label

_ilabelModel = None

AUTO_ID_PREFIX = "label2d_id_"
class IlabelModel(PythonModel):
	def __init__(self):
		global _ilabelModel
		if _ilabelModel:
			raise RuntimeError(
				"attempt to create second IlabelModel instance")
		_ilabelModel = self
		PythonModel.__init__(self)
		self.labels = []
		self.labelMap    = {}
		self._UID        = 0
		self.curLabel = None
		chimera.openModels.add([self], baseId=-1, hidden=True)
		self._sessionHandlerID = chimera.triggers.addHandler(
					SAVE_SESSION, self._saveSession, None)
	def destroy(self, *args):
		for label in self.labels:
			label.destroy()
		chimera.triggers.deleteHandler(SAVE_SESSION,
							self._sessionHandlerID)
		PythonModel.destroy(self, True)
		global _ilabelModel
		_ilabelModel = None

	def computeBounds(self, sphere, bbox):
		return False

	def validXform(self):
		return False

	def draw(self, lens, viewer, passType):
		if passType != chimera.LensViewer.Overlay2d:
			return

		w, h = viewer.windowSize
		curFont = None
		for label in self.labels:
			baseX, baseY = label.pos[0]*w, label.pos[1]*h
			# looks less fuzzy on integer boundaries
			baseX = int(baseX + 0.5)
			baseY = int(baseY + 0.5)
			# TODO: handle justify
			# style (justify is only left/center/right)
			# any changes here need to mirror in pickLabel
			# and x3dWrite
			if not unicode(label) or not label.shown:
				continue
			for line in label.lines:
				width = 0.0
				for c in line:
					#GL.glRasterPos3f(baseX + width,
					#			baseY, 0.0)
					#viewer.rasterPos3(baseX + width,
					#			baseY, 0.0)
					GL.glPushMatrix()
					GL.glTranslatef(baseX + width,
								baseY, 0.0)
					# font setup/teardown is expensive
					# so minimize it as much as possible
					if curFont is None or c.font != curFont:
						if curFont is not None:
							curFont.cleanup()
						curFont = c.font
						curFont.setup()
					curFont.setColor(*c.rgba)
					text = unicode(c)
					curFont.draw(text)
					width += curFont.width(text)
					GL.glPopMatrix()
				if curFont:
					fsize = curFont.size()
				else:
					fsize = 24
				baseY -= fsize * \
					chimera.LODControl.get().fontAdjust()
		if curFont is not None:
			curFont.cleanup()

	def x3dNeeds(self, scene):
		if not self.labels:
			return

		scene.needComponent(chimera.X3DScene.Text, 1)

	def x3dWrite(self, indent, scene):
		if not self.labels:
			return

		# repeat draw code, but output x3d
		w, h = chimera.viewer.windowSize
		prefix = ' ' * indent
		curFont = None
		fontCount = 0
		output = []
		FONTDEF = "<FontStyle DEF='ILabel%s' family='%s' size='%s' style='%s'>\n"
		ENDFONTDEF = "</FontStyle>\n"
		FONTUSE = "<FontStyle USE='ILabel%s'/>\n"
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
		cam = chimera.viewer.camera
		view = 0
		eyePos = cam.eyePos(view)
		left, right, bottom, top, hither, yon, focal = cam.window(view)
		scale = (right - left) / w
		xlate_scale = (eyePos[0] + left, eyePos[1] + bottom, eyePos[2] - hither, scale, scale, 1)
		output.extend([
			prefix, OVERLAY,
			prefix, TRANSCALE % xlate_scale
			])
		hasLabels = False
		for label in self.labels:
			if not unicode(label) or not label.shown:
				continue
			hasLabels = True
			baseX, baseY = label.pos[0]*w, label.pos[1]*h
			# looks less fuzzy on integer boundaries
			baseX = int(baseX + 0.5)
			baseY = int(baseY + 0.5)
			for line in label.lines:
				width = 0.0
				for c in line:
					output.extend([prefix, ' ',
						TRANS % (baseX + width, baseY,
									0)])
					output.extend([prefix, '  ', SHAPE])
					output.extend([prefix, '   ', APPEAR])
					if c.rgba[3] != 1:
						rgbt = c.rgba[0:3] + (1 - c.rgba[3],)
						output.extend([prefix, '   ',
							MATTRANS % rgbt])
					else:
						output.extend([prefix, '   ',
							MAT % c.rgba[0:3]])
					output.extend([prefix, '   ',
								ENDAPPEAR])
					text = unicode(c)
					output.extend([prefix, '   ',
						TEXT % chimera.xml_quote(text)])
					if curFont is None or c.font != curFont:
						fontCount += 1
						curFont = c.font
						output.extend([
							prefix, '    ', FONTDEF
							% (fontCount,
							curFont.x3dFamily(),
							curFont.size(),
							curFont.x3dStyle()),
							prefix, '     ',
							FILENAME %
							curFont.filename(),
							prefix, '    ',
							ENDFONTDEF
							])
					else:
						output.extend([prefix, '    ',
							FONTUSE % fontCount])
					width += curFont.width(text)
					output.extend([prefix, '   ', ENDTEXT])
					output.extend([prefix, '  ', ENDSHAPE])
					output.extend([prefix, ' ', ENDTRANS])
				baseY -= curFont.size()
		output.extend([prefix, ENDTRANS])
		if not hasLabels:
			return ""
		return ''.join(output)

	def changeLabel(self, newText):
		self.curLabel.set(newText)
		self.setMajorChange()

	def changeToLabel(self, nextLabel):
		self.curLabel = nextLabel

	def moveLabel(self, pos):
		self.curLabel.pos = pos
		self.setMajorChange()

	def _getLabelID(self):
		## start critical section
		_uidLock.acquire()
		id = self._UID
		self._UID += 1
		_uidLock.release()
		## end critical section
		
		return AUTO_ID_PREFIX + "%s" % id
		
	def newLabel(self, pos, labelID=None):
		
		if labelID:
			if labelID in self.labelMap.keys():
				raise RuntimeError("Already have a label " \
						   "with ID '%s'" % labelID
						   )
			else:
				l_id = labelID
		else:
			l_id = self._getLabelID()

		newLabel = Label(pos, self)
		self.labels.append(newLabel)

		self.labelMap[l_id] = newLabel

		return newLabel

	def pickLabel(self, pos, w, h):
		slop = 2
		targetX, targetY = pos[0]*w, pos[1]*h
		for label in self.labels:
			if not unicode(label) or not label.shown:
				continue
			baseX, baseY = label.pos[0]*w, label.pos[1]*h
			font = None
			for line in label.lines:
				width = 0.0
				for c in line:
					font = c.font
					lx = baseX + width - slop
					text = unicode(c)
					width += font.width(text)
					rx = baseX + width + slop
					above, below = font.height(text)
					uy = baseY + above + slop
					ly = baseY + below - slop
					if targetX >= lx and targetX <= rx \
					and targetY >= ly and targetY <= uy:
						moveOffset = (
							targetX - baseX,
							targetY - label.pos[1]*h
						)
						break
				else:
					if font:
						baseY -= font.size()
					else:
						baseY -= 24
					continue
				break
			else:
				continue
			break
		else:
			label = None
			moveOffset = (0, 0)
		return label, moveOffset

	def removeLabel(self, label):
		self.labels.remove(label)

		for k,v in self.labelMap.items():
			if v == label:
				del self.labelMap[k]
				break
			
		if label == self.curLabel:
			self.curLabel = None
		if unicode(label):
			self.setMajorChange()
		label.destroy()

	def _restoreSession(self, info):
		for labelInfo in info["labels"]:
			new_label = Label(*(labelInfo["args"] + (self,)))
			self.labels.append(new_label)
			self.labels[-1]._restoreSession(labelInfo)

		if info.has_key("labelUID"):
			self._UID = info["labelUID"]

		for idx,label in enumerate(self.labels):
			if info.has_key("labelIDs"):
				uid = info["labelIDs"][idx]
			else:
				uid = self._getLabelID()
			self.labelMap[uid] = label

		if info["curLabel"] is None:
			self.curLabel = None
		else:
			self.curLabel = self.labels[info["curLabel"]]

	def _saveSession(self, triggerName, myData, sessionFile):
		if self.curLabel:
			pos = "il.labels[%d]" % self.labels.index(self.curLabel)
		else:
			pos = "None"
		print>>sessionFile, """
try:
	import Ilabel
	if Ilabel._ilabelModel:
		Ilabel._ilabelModel.destroy()
	from Ilabel.Label import Label, Character
	il = Ilabel.IlabelModel()
	il._restoreSession(%s)
	del Ilabel, Label, Character, il
except:
	reportRestoreError("Error restoring IlabelModel instance in session")
""" % repr(self._sessionInfo())

	def _sessionInfo(self):
		info = {}
		info["labels"]   = [l._sessionInfo() for l in self.labels]

		id_list = []
		for l in self.labels:
			## try to find the label as a value in the labelMap,
			## and add the key to id_list
			for k,v in self.labelMap.items():
				if v == l:
					id_list.append(k)
					break
			## this case should never happen, but if labelMap
			## somehow became corrupted, come up with a new
			## id for this label, and add append it to id_list
			else:
				id_list.append(self._getLabelID()) 

		info["labelIDs"] = id_list

		info["labelUID"] = self._UID
		
		if self.curLabel:
			info["curLabel"] = self.labels.index(self.curLabel)
		else:
			info["curLabel"] = None
		
		return info


## this map serves as a temporary scratchspace for cacheing the opacity
## of a label. This is necessary when you want to 'hide' a label over
## several frames (i.e. a fade-to-black): first, you cache the current
## opacity of the label (keyed by the label instance). Then register the
## _addMotionHandler for the _fade command. If the label being _faded has
## an entry in the opacityCache, it restores the original opacity on the
## last iteration of _fade, then un-shows the label using a call to
## setShowLabel
opacityCache = {}

def processLabel2DCmd(action, labelID, text=None, color=None, size=None, style=None,
	typeface=None, xpos=None, ypos=None, visibility=None, frames=None):
    
	from Midas import MidasError

	if type(xpos) == list or type(ypos) == list:
		raise MidasError("Multiple occurances of 'xpos' or 'ypos' keywords")

	try:
		if xpos: xpos + 0
		if ypos: ypos + 0
	except:
		raise MidasError("xpos/ypos values must be numeric")

	global _ilabelModel
	if not _ilabelModel:
		IlabelModel()
	model = _ilabelModel

	if text is not None:
		# text might have evaluated as an integer or something
		text = unicode(text)

		# backslash interpretation...
		if '\\' in text:
			if '"' not in text:
				text = eval('"' + text + '"')
			elif "'" not in text:
				text = eval("'" + text + "'")

	if action == "create":
		## get the position
		if xpos==None:
			xpos = .5
		if ypos==None:
			ypos = .5

		if not color:
			color = chimera.Color.lookup('white')
		
		if not size:
			size = 24

		if not style:
			style = "normal"
			
		if not typeface:
			typeface = "sans serif"

		## make a new label
		try:
			label = model.newLabel( (xpos,ypos), labelID )
		except RuntimeError, what:
			raise MidasError, what
		
		## set it's content
		label.set(text or '')

		## color and size the characters
		changeLabelAttrs(label, size, color, styleLookup(style),
						typefaceLookup(typeface))

		if visibility == "hide":
			label.shown = False

	elif action == "change":
		if not model.labelMap.has_key(labelID):
			raise MidasError, "No such label with ID '%s'" % labelID

		label = model.labelMap[labelID]

		if text!=None:
			cur_size  = None
			cur_color = None
			cur_style = None
			cur_typeface = None
			
			if (len(label.lines) > 0) and \
			   (len(label.lines[0]) > 0):
				c = label.lines[0][0]
				cur_color = c.rgba
				cur_size  = c.size
				cur_style = c.style
				cur_typeface = c.fontName

			label.set(text)

			if cur_color:
				cur_color = chimera.MaterialColor(*cur_color)

			changeLabelAttrs(label, cur_size, cur_color, cur_style,
								cur_typeface)

		if color or size or style or typeface:
			if style:
				style = styleLookup(style)
			if typeface:
				typeface = typefaceLookup(typeface)
			changeLabelAttrs(label, size, color, style, typeface)

		if (xpos!=None) or (ypos!=None):
			cur_xpos, cur_ypos = label.pos
			if xpos==None: xpos = cur_xpos
			if ypos==None: ypos = cur_ypos
			label.pos = (xpos, ypos)

		if visibility:
			from Midas import _addMotionHandler

			global _tickMotionHandler
			from Midas import _tickMotionHandler
			
			
			param = {'command':'fade','label':label,
				'frames':frames}
			## need step, frames

			cur_a = getLabelColor(label)[3]
			
			if visibility == 'show':
				if not frames:
					label.shown = True
					## dont need to check opacityCache when
					## showing; if opacity of a label was
					## changed in order to do a fade-hide,
					## it would have been restored on the
					## final iteration of the _fade method
				else:
					## should show start from 0?  Is wierd
					## when someone 'shows' a label that is
					## already shown
					changeLabelAttrs(label, opacity=0.0)
					label.shown = True
					step = (cur_a) / frames
					param['step'] = step
					_addMotionHandler(_fade, param)
					
			elif visibility == 'hide':
				if not frames:
					label.shown = False
					#changeLabelAttrs(label, opacity=0.0)
				else:
					## set opacityCache when hiding.
					opacityCache[label] = cur_a
					step = cur_a / frames
					param['step'] = -(step)
					_addMotionHandler(_fade, param)
			else:
				raise MidasError, "No such visibility mode '%s'" % visibility

	elif action == "delete":
		if not model.labelMap.has_key(labelID):
			raise MidasError, "No such label with ID '%s'" % labelID

		label = model.labelMap[labelID]
		model.removeLabel(label)

	elif action == "read":
		readFiles([labelID])

	elif action == "write":
		writeFile(labelID)

	else:
		raise MidasError, "Unknown 2dlabels action '%s'" % action

	model.setMajorChange()
	from gui import IlabelDialog
	from chimera import dialogs
	dlg = dialogs.find(IlabelDialog.name)
	if dlg:
		dlg.updateGUI("command")

def changeLabelAttrs(label, size=None, color=None, style=None, typeface=None,
							opacity=None):
		
	chars = []
	[chars.extend(line) for line in label.lines]

	for c in chars:
		if color != None:
			c.rgba = color.rgba()[0:3] + (c.rgba[3],)
		if size != None:
			c.size = size
		if style != None:
			c.style = style
		if typeface != None:
			c.fontName = typeface
		if opacity != None:
			if opacity < 0.0:
				opacity = 0.0
			elif opacity > 1.0:
				opacity = 1.0
			c.rgba = c.rgba[0:3] + (opacity,)

def getLabelColor(label):
	chars = []
	[chars.extend(line) for line in label.lines]

	if len(chars) == 0:
		return (1.0, 1.0, 1.0, 1.0)
	else:
		return chars[0].rgba

def readFiles(fileNames, clear=True):
	if not _ilabelModel:
		IlabelModel()
	if clear:
		for label in _ilabelModel.labels[:]:
			_ilabelModel.removeLabel(label)
	_ilabelModel.setMajorChange()
	from chimera import UserError
	for fileName in fileNames:
		from OpenSave import osOpen
		f = osOpen(fileName)
		label = labelID = text = None
		for ln, line in enumerate(f):
			lineNum = ln + 1
			if not line.strip() or line.strip().startswith('#'):
				# skip blank lines / comments
				continue
			if line.lower().startswith("label"):
				labelID = line[5:].strip()
				continue
			if line[0] != '\t':
				f.close()
				raise UserError("%s, line %d: line must start with 'Label'"
					" or tab" % (fileName, lineNum))
			try:
				semi = line.index(':')
			except ValueError:
				f.close()
				raise UserError("%s, line %d: line must have semi-colon"
					% (fileName, lineNum))
			name = line[1:semi].lower()
			if not label and name != "(x,y)":
				f.close()
				raise UserError("%s, line %d: xy position must immediately"
					" follow 'Label' line" % (fileName, lineNum))
			if label and text is None and name != "text":
				f.close()
				raise UserError("%s, line %d: text must immediately"
					" follow xy position" % (fileName, lineNum))
			value = line[semi+1:].strip()
			if name == "(x,y)":
				text = None
				try:
					pos = eval(value)
				except:
					f.close()
					raise UserError("%s, line %d: could not parse xy value"
						% (fileName, lineNum))
				if labelID:
					label = _ilabelModel.newLabel(pos)
				else:
					label = _ilabelModel.newLabel(pos, labelID=labelID)
			elif name == "text":
				try:
					text = eval(value)
				except:
					f.close()
					_ilabelModel.removeLabel(label)
					raise UserError("%s, line %d: could not parse 'text' value"
						% (fileName, lineNum))
				label.set(text)
			elif name == "shown":
				if name == "shown":
					try:
						label.shown = eval(value.capitalize())
					except:
						f.close()
						_ilabelModel.removeLabel(label)
						raise UserError("%s, line %d: could not parse 'shown'"
							" value" % (fileName, lineNum))
			else:
				chars = []
				for l in label.lines:
					chars.extend(l)
				if '),' in value:
					values = value.split('),')
					for i, v in enumerate(values[:-1]):
						values[i] = v + ')'
				elif ',' in value and not value.strip().startswith('('):
					values = value.split(',')
				else:
					values = [value] * len(chars)
				if len(values) != len(chars):
					f.close()
					raise UserError("%s, line %d: number of values not equal"
						" to numbers of characters in text (and not a single"
						" value)" % (fileName, lineNum))
				if name.startswith("font size"):
					try:
						values = [eval(v) for v in values]
					except:
						f.close()
						_ilabelModel.removeLabel(label)
						raise UserError("%s, line %d: could not parse"
							" 'font size' value(s)" % (fileName, lineNum))
					for c, v in zip(chars, values):
						c.size = v
				elif name.startswith("font style"):
					for c, v in zip(chars, values):
						try:
							c.style = styleLookup(v.strip().lower())
						except:
							f.close()
							_ilabelModel.removeLabel(label)
							raise UserError("%s, line %d: could not parse"
								" 'font style' value(s)" % (fileName, lineNum))
				elif name.startswith("font typeface"):
					for c, v in zip(chars, values):
						try:
							c.fontName = typefaceLookup(v.strip().lower())
						except:
							f.close()
							_ilabelModel.removeLabel(label)
							raise UserError("%s, line %d: could not parse"
								" 'font typeface' value(s)" %
								(fileName, lineNum))
				elif name.startswith("color"):
					try:
						values = [eval(v) for v in values]
					except:
						f.close()
						_ilabelModel.removeLabel(label)
						raise UserError("%s, line %d: could not parse"
							" 'color' value(s)" % (fileName, lineNum))
					for c, v in zip(chars, values):
						c.rgba = v
				else:
					_ilabelModel.removeLabel(label)
					raise UserError("%s, line %d: unknown label attribute '%s'"
						% (fileName, lineNum, name))
		f.close()
	if chimera.nogui:
		dlg = None
	else:
		from gui import IlabelDialog
		from chimera import dialogs
		dlg = dialogs.find(IlabelDialog.name)
	if dlg:
		dlg.updateGUI("file")

FONT_STYLE_LABELS = ["normal", "italic", "bold", "bold italic"]
oglFont = chimera.OGLFont
FONT_STYLE_VALUES = [oglFont.normal, oglFont.italic, oglFont.bold,
					oglFont.bold | oglFont.italic]
def styleLookup(label):
	try:
		return FONT_STYLE_VALUES[FONT_STYLE_LABELS.index(label)]
	except ValueError:
		from Midas import MidasError
		raise MidasError("No known font style '%s'; choices are: %s" %
			(label, ", ".join(FONT_STYLE_LABELS)))

FONT_TYPEFACE_LABELS = ["sans serif", "serif", "fixed"]
FONT_TYPEFACE_VALUES = ["Sans Serif", "Serif", "Fixed"]
def typefaceLookup(label):
	try:
		return FONT_TYPEFACE_VALUES[FONT_TYPEFACE_LABELS.index(label)]
	except ValueError:
		from Midas import MidasError
		raise MidasError("No known font typeface '%s'; choices are: %s"
			% (label, ", ".join(FONT_TYPEFACE_LABELS)))

def writeFile(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, 'w')
	if _ilabelModel:
		labelIDs = _ilabelModel.labelMap.keys()
		labelIDs.sort()
		for labelID in labelIDs:
			if labelID.startswith(AUTO_ID_PREFIX):
				print>>f, "Label"
			else:
				print>>f, "Label %s" % labelID
			label = _ilabelModel.labelMap[labelID]
			print>>f, "\t(x,y): %s" % repr(label.pos)
			print>>f, "\ttext: %s" % repr(unicode(label))
			print>>f, "\tshown: %s" % label.shown
			print>>f, "\tfont size(s): %s" % _valuesString([str(c.size)
									for l in label.lines for c in l])
			print>>f, "\tfont style(s): %s" % _valuesString([
				FONT_STYLE_LABELS[FONT_STYLE_VALUES.index(c.style)]
									for l in label.lines for c in l])
			print>>f, "\tfont typeface(s): %s" % _valuesString([
				FONT_TYPEFACE_LABELS[FONT_TYPEFACE_VALUES.index(c.fontName)]
									for l in label.lines for c in l])
			print>>f, "\tcolor(s): %s" % _valuesString([repr(c.rgba)
									for l in label.lines for c in l])
	f.close()

def _fade(trigger, param, triggerData):
	global _ilabelModel
	
	if trigger:
		_tickMotionHandler(param)

	step  = param['step']
	label = param['label']

	cur_a = getLabelColor(label)[3]
	changeLabelAttrs(label, opacity=cur_a+step)
	_ilabelModel.setMajorChange()

	if step < 0 and param['frames'] == 0:
		## means this is the last iteration of a fade to black
		## after you fade it, need to set it back to former opacity !!
		label.shown = False
		global opacityCache
		if opacityCache.has_key(label):
			changeLabelAttrs(label, opacity=opacityCache[label])
			del opacityCache[label]

def _valuesString(values):
	if len(set(values)) == 1:
		return values[0]
	return ", ".join(values)
