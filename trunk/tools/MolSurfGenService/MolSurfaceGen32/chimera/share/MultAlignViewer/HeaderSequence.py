# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: HeaderSequence.py 29134 2009-10-23 22:03:08Z pett $

"""header sequence classes/functions"""

from chimera.Sequence import Sequence

class HeaderSequence(Sequence):
	# sortVal determines the default ordering of headers.
	# Built-in headers change their sortVal to a value in the range
	# [1.0, 2.0) so they normally appear before registered headers.
	# Identical sortVals tie-break on sequence name.
	sortVal = 2.0
	def __init__(self, mav, name=None, evalWhileHidden=False):
		Sequence.__init__(self, name=name)
		from weakref import proxy
		self.mav = proxy(mav)
		self.visible = False
		self.evalWhileHidden = evalWhileHidden

	def alignChange(self, left, right):
		"""alignment changed in positions from 'left' to 'right'"""
		for pos in range(left, right+1):
			self[pos] = self.evaluate(pos)

	def destroy(self):
		pass

	def evaluate(self, pos):
		raise NotImplementedError("evaluate() method must be"
			" implemented by %s subclass" % self.__class__.__name__)

	def fastUpdate(self):
		# if asked to update a few columns (alignChange() method)
		# can it be done quickly?
		return True

	def hide(self):
		"""Called when sequence hidden"""
		self.visible = False

	def histInfinity(self, position):
		"""convenience function to map arbitrary number to 0-1 range

		   used in the 'depictionVal' method for some kinds of data
		"""
		raw = self[position]
		if raw is None:
			return 0.0
		from math import exp
		if raw >= 0:
			return 1.0 - 0.5 * exp(-raw)
		return 0.5 * exp(raw)

	def positiveHistInfinity(self, position):
		"""convenience function to map arbitrary positive number to 0-1 range

		   used in the 'depictionVal' method for some kinds of data
		"""
		raw = self[position]
		if raw is None:
			return 0.0
		from math import exp
		return 1.0 - exp(-raw)

	def reevaluate(self):
		"""sequences changed, possibly including length"""
		self[:] = []
		for pos in range(len(self.mav.seqs[0])):
			self.append(self.evaluate(pos))
	def show(self):
		"""Called when sequence shown"""
		self.visible = True

class FixedHeaderSequence(HeaderSequence):

	# header relevant if alignment is a single sequence?
	singleSequenceRelevant = True

	def __init__(self, name, mav, val):
		self.val = val
		HeaderSequence.__init__(self, mav, name=name)
		self.reevaluate()
	
	def alignChange(self, left, right):
		pass
	
	def reevaluate(self):
		if len(self.mav.seqs[0]) == len(self.val):
			self[:] = self.val
			if hasattr(self, "saveColorFunc"):
				self.colorFunc = self.saveColorFunc
				delattr(self, "saveColorFunc")
		else:
			self[:] = '?' * len(self.mav.seqs[0])
			if hasattr(self, "colorFunc") \
			and not hasattr(self, "saveColorFunc"):
				self.saveColorFunc = self.colorFunc
				self.colorFunc = lambda s, o: 'black'

class DynamicHeaderSequence(HeaderSequence):

	# header relevant if alignment is a single sequence?
	singleSequenceRelevant = False

	def __init__(self, *args, **kw):
		HeaderSequence.__init__(self, *args, **kw)
		self.__handlerID = None
		self._needUpdate = True
		if self.evalWhileHidden:
			self.reevaluate()
			from MAViewer import ADDDEL_SEQS
			self.__handlerID = self.mav.triggers.addHandler(
						ADDDEL_SEQS, self.refresh, None)

	def destroy(self):
		if self.__handlerID != None:
			from MAViewer import ADDDEL_SEQS
			self.mav.triggers.deleteHandler(ADDDEL_SEQS,
							self.__handlerID)
			self.__handlerID = None
		HeaderSequence.destroy(self)

	def refresh(self, *args, **kw):
		if self.visible or self.evalWhileHidden:
			self.reevaluate()
			if not kw.get('fromShow', False):
				self.mav.refreshHeader(self)
			self._needUpdate = False
		else:
			self._needUpdate = True

	def show(self):
		HeaderSequence.show(self)
		if self.evalWhileHidden:
			return
		if self._needUpdate:
			self.refresh(fromShow=True)
		if self.__handlerID == None:
			from MAViewer import ADDDEL_SEQS
			self.__handlerID = self.mav.triggers.addHandler(
					ADDDEL_SEQS, self.refresh, None)

	def hide(self):
		HeaderSequence.hide(self)

class DynamicStructureHeaderSequence(DynamicHeaderSequence):
	def __init__(self, *args, **kw):
		DynamicHeaderSequence.__init__(self, *args, **kw)
		self.__handlerID = None

	def destroy(self):
		if self.__handlerID != None:
			from MAViewer import MOD_ASSOC
			self.mav.triggers.deleteHandler(MOD_ASSOC,
							self.__handlerID)
			self.__handlerID = None
		DynamicHeaderSequence.destroy(self)

	def show(self):
		DynamicHeaderSequence.show(self)
		if self.__handlerID == None:
			from MAViewer import MOD_ASSOC
			self.__handlerID = self.mav.triggers.addHandler(
					MOD_ASSOC, self.refresh, None)

	def hide(self):
		DynamicHeaderSequence.hide(self)

registeredHeaders = {}
def registerHeaderSequence(seq, defaultOn=True):
	registeredHeaders[seq] = defaultOn
