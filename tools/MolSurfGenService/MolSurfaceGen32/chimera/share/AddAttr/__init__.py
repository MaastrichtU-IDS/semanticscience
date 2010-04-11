# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera import replyobj, selection, specifier, misc
from Midas.midas_text import convertType

_MATCH_MODE_1_TO_1 = "1-to-1"
_MATCH_MODE_NON_ZERO = "non-zero"
_MATCH_MODE_ANY = "any"
_matchModes = [ _MATCH_MODE_1_TO_1, _MATCH_MODE_NON_ZERO, _MATCH_MODE_ANY ]

def addAttributes(attrFile, models=None, log=False, raiseAttrDialog=True):
	"""add/set attributes from a file

	   'attrFile' indicates a file path or an opened file object.  The
	   file contains control lines and data lines.  Control and data lines
	   may be freely interspersed.  The data lines are of the form:

	   	<tab>selector<tab>attribute value

	   The selector is an atom specification (as per the Atom Specification
	   section of the User's Guide).  The attribute value is a boolean,
	   integer, float, or string.  If it is necessary to specify a string
	   attribute that could be interpreted as one of the other types,
	   embed the value in double quotes (it will then be evaluated as a
	   Python string, including backslash interpretation).

	   The control lines are of the form:

	   	name: value
	   
	   The possible name/value pairs are:

	   	Name         Value
		----         -----
		attribute    name of the attribute to assign to
		match mode   expected matches per selector:
		                "1 to 1":  exactly one match per selector
				"non-zero":  at least one match per selector
				"any":  no constraint
			     selectors not conforming to the match mode will
			     generate an error
		recipient    where to put attribute (atoms/residues/molecules)
	   
	   The only mandatory control line is 'attribute', which must precede
	   any data lines.  The default match mode is 1 to 1, and the default
	   recipient is atoms.

	   Empty lines are ignored and lines beginning with the '#' character
	   are considered comments and ignored.

	   'log' controls whether information about what each selector matched
	   is sent to the reply log.

	   'models' restricts any selector matching to the given models.  If
	   'models' is None, then no restriction occurs.

	   This function return a list of recipient/attribute tuples that
	   actually were set in at least one object.  If an error occurred,
	   None is returned instead.
	"""

	from OpenSave import osOpen
	try:
		if isinstance(attrFile, basestring):
			attrFile = osOpen(attrFile)
			try:
				return _addAttr(attrFile, models, log,
								raiseAttrDialog)
			finally:
				attrFile.close()
		else:
			return _addAttr(attrFile, models, log, raiseAttrDialog)
	except SyntaxError, v:
		replyobj.error(str(v) + "\n")
		return None

def _addAttr(attrFile, models, log, raiseAttrDialog):
	setAttrs = {}
	colors = {}

	from CGLutil.annotatedDataFile import readDataFile
	control = { 'match mode': _MATCH_MODE_ANY, 'recipient': "atoms" }
	for rawControl, data in readDataFile(attrFile):
		control.update(rawControl)

		legalNames = ["attribute", "match mode", "recipient"]
		for name in control.keys():
			if name not in legalNames:
				raise SyntaxError("Unknown name part of control"
					" line: '%s'\nMust be one of: %s" % (
					name, ", ".join(legalNames)))

		if "attribute" not in control:
			raise SyntaxError("No attribute name specified in file")
		attrName = control["attribute"]
		if not attrName.replace("_", "").isalnum() \
		or attrName[0].isdigit():
			raise SyntaxError("Attribute name (%s) is bad.\n"
				"It must be strictly alphanumeric characters or"
				" underscores with no spaces and must not start"
				" with a digit." % control["attribute"])
		colorAttr = attrName.lower().endswith("color")

		matchMode = control["match mode"]
		if matchMode not in _matchModes:
			raise SyntaxError("Unknown match mode (%s) specified.\n"
				"It must be one of: %s" % (
				control["match mode"], ", ".join(_matchModes)))

		recipient = control["recipient"]
		if not hasattr(selection.ItemizedSelection, recipient):
			raise SyntaxError("Unknown attribute recipient (%s)"
				" specified.\nSuggest using atoms, residues, or"
				" molecules" % control["recipient"])
		dataErrors = []
		for lineNum, d in enumerate(data):
			try:
				selector, value = d
			except ValueError:
				dataErrors.append("Data line %d of file either"
					" not selector/value or not"
					" tab-delimited" % (lineNum+1))
				continue

			try:
				sel = specifier.evalSpec(selector, models)
			except:
				import sys
				dataErrors.append("Mangled selector (%s) on"
					" data line %d: %s" % (selector,
					lineNum+1, sys.exc_value))
				continue
			matches = getattr(sel, recipient)()
			# restrict to models; the "models" argument to evalSpec
			# only works if the selector is an OSL
			if matches and models is not None:
				md = set(models)
				level = matches[0].oslLevel()
				if level == selection.SelGraph:
					filterFunc = lambda x, md=md: x in md
				elif level == selection.SelEdge:
					filterFunc = lambda x, md=md: \
						x.atoms[0].molecule in md
				else:
					filterFunc = lambda x, md=md: \
							x.molecule in md
				matches = filter(filterFunc, matches)
			if not matches:
				if matchMode != _MATCH_MODE_ANY:
					dataErrors.append("Selector (%s) on"
						" data line %d matched nothing"
						% (selector, lineNum+1))
					continue
			elif len(matches) > 1:
				if matchMode == _MATCH_MODE_1_TO_1:
					dataErrors.append("Selector (%s) on"
						" data line %d matched multiple"
						" items: %s" % (selector,
						lineNum+1, ", ".join(map(lambda
						m: m.oslIdent(), matches))))
			if log:
				replyobj.info("Selector %s matched " % selector
					+ ", ".join(map(misc.chimeraLabel,
					matches)) + "\n")
			if colorAttr:
				if value[0].isalpha():
					# color name
					from chimera.colorTable \
							import getColorByName
					try:
						value = getColorByName(value)
					except KeyError:
						dataErrors.append("Unknown"
							" color name on data"
							" line %d: '%s'" %
							(lineNum+1, value))
						continue
				else:
					try:
						rgba = tuple(map(float,
								value.split()))
					except ValueError:
						dataErrors.append(
							"Unrecognizable color"
							" value on data line"
							" %d: '%s'; Must be"
							" either color name or"
							" 3 or 4 numbers"
							" between 0 and 1"
							" (RGBA)" % (lineNum+1))
						continue
					if max(rgba) > 1.0 or min(rgba) < 0.0:
						dataErrors.append("Color"
							" component values on"
							" data line %d not"
							" in the range 0 to 1"
							% (lineNum+1))
						continue
					if rgba in colors:
						value = colors[rgba]
					elif len(rgba) in [3, 4]:
						value = chimera.MaterialColor(
									*rgba)
						colors[rgba] = value
					else:
						dataErrors.append("Bad number"
							" of color components"
							" on data line %d; Must"
							" be either 3 or 4 (was"
							" %d)" % (lineNum+1,
							len(rgba)))
						continue
			else:
				value = convertType(value)
			for match in matches:
				setattr(match, attrName, value)
			if matches and not colorAttr:
				setAttrs[(recipient, attrName)] = value
	recipMapping = {
		"molecules": chimera.Molecule,
		"residues": chimera.Residue,
		"bonds": chimera.Bond,
		"atoms": chimera.Atom
	}
	from SimpleSession import registerAttribute
	for recipient, attrName in setAttrs:
		if recipient in recipMapping:
			registerAttribute(recipMapping[recipient], attrName)
	if setAttrs and not chimera.nogui and raiseAttrDialog:
		from ShowAttr import ShowAttrDialog, screenedAttrs
		from chimera import dialogs
		showableAttr = False
		reasons = []
		for recipient, attrName in setAttrs.keys():
			if recipient == "molecules":
				recipient = "models"

			validRecipients = ["atoms", "residues", "models"]
			if recipient not in validRecipients:
				reasons.append("%s not assigned to atoms,"
					" residues, or models" % attrName)
				continue
			key = [chimera.Atom, chimera.Residue, chimera.Model][
					validRecipients.index(recipient)]
			if attrName in screenedAttrs[key]:
				reasons.append("%s automatically screened out"
					" by Render By Attribute" % attrName)
				continue
			if attrName[0] == '_':
				reasons.append("%s considered to be a private"
					" variable" % attrName)
				continue
			if attrName[0].isupper():
				reasons.append("%s considered to be a symbolic"
					" constant due to initial capital"
					" letter" % attrName)
				continue
			showableAttr = True
			break
			
		if showableAttr:
			if models is None:
				ms = chimera.openModels.list()
			else:
				ms = models
			if colorAttr:
				an = None
				mode = None
			else:
				an = attrName
				from types import StringTypes
				if type(setAttrs[(recipient, attrName)]) in (
							bool,) + StringTypes:
					mode = "Select"
				else:
					mode = "Render"
			d = dialogs.display(ShowAttrDialog.name)
			d.configure(models=[m for m in ms
				if isinstance(m, chimera.Molecule)],
				attrsOf=recipient, attrName=an, mode=mode)
		else:
			replyobj.warning("No attributes usable by Render dialog"
				" were defined:\n" + "\n".join(reasons) + "\n")
	if dataErrors:
		raise SyntaxError, "\n".join(dataErrors)
	return setAttrs
