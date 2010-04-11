# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: triggerSet.py 26655 2009-01-07 22:02:30Z gregc $

"""
triggerSet module

This module defines one class, TriggerSet, which implements a simple callback
mechanism.  A TriggerSet instance contains a set of named triggers, each of
which may have a number of handlers registered with it. Activating a trigger
in the instance causes all its handlers to be called, in the order of
registration.

Example

The following example creates a TriggerSet instance named ts and adds a
trigger named conrad. Two handlers are registered: the first reports its
arguments; the second reports its arguments and then deregisters itself.

import triggerSet

ts = triggerSet.TriggerSet()
ts.addTrigger('conrad')

def first(trigger, funcData, triggerData):
	print 'trigger =', trigger, 'funcData =', funcData, \
		'triggerData =', triggerData

def second(trigger, dict, triggerData):
	print 'trigger =', trigger, \
		'triggerSet =', dict['triggerSet'], \
		'handler =', dict['handler'], \
		'triggerData =', triggerData
	dict['triggerSet'].deleteHandler(trigger, dict['handler'])

h1 = ts.addHandler('conrad', first, 'argument')
a2 = {'triggerSet':ts}
a2['handler'] = ts.addHandler('conrad', second, a2)

ts.activateTrigger('conrad', 1)
print
ts.activateTrigger('conrad', 2)

The output from this example is: 

trigger = conrad funcData = argument triggerData = 1
trigger = conrad triggerSet = <triggerSet.TriggerSet instance at 1400f3010> handler = <triggerSet._TriggerHandler instance at 140097ac0> triggerData = 1

trigger = conrad funcData = argument triggerData = 2

Note that the value of handler arguments may be changed even after the
handler was registered. In the above example, an additional value,
handler, was added to the dictionary argument to the second handler
after registration. 

If a handler returns the value TriggerSet.ONESHOT, then the handler will
be deregistered after it returns.  Therfore, the 'second()' function 
above could have been written more simply as:

def second(trigger, dict, triggerData):
	print 'trigger =', trigger, \
		'triggerSet =', dict['triggerSet'], \
		'handler =', dict['handler'], \
		'triggerData =', triggerData
	return TriggerSet.ONESHOT
"""

ONESHOT = "oneshot"

class _TriggerHandler:
	"""Describes callback routine registered with _Trigger"""

	def __init__(self, func, funcData):
		self._func = func
		self._funcData = funcData

	def invoke(self, triggerName, triggerData):
		import chimera
		try:
			return self._func(triggerName,
						self._funcData, triggerData)
		except chimera.ChimeraSystemExit:
			raise
		except chimera.UserError:
			from chimera.replyobj import reportException
			reportException()
		except:
			from chimera.replyobj import reportException
			reportException('Error processing trigger "%s"'
								% triggerName)
class _Trigger:
	"""Keep track of handlers to invoke when activated"""

	def __init__(self, triggerName, usageCB):
		self._name = triggerName
		self._handlerList = []
		self._addList = []
		self._delList = []
		self._locked = 0
		self._blocked = 0
		self._needActivate = 0
		self._needActivateMap = {}
		self._needActivateData = []
		self._usageCB = usageCB

	def add(self, handler):
		if self._locked:
			self._addList.insert(0, handler)
		else:
			self._handlerList.insert(0, handler)
		if self._usageCB \
		and len(self._addList) + len(self._handlerList) == 1:
			self._usageCB(self._name, 1)

	def delete(self, handler):
		if self._locked:
			try:
				self._addList.remove(handler)
			except ValueError:
				if handler not in self._delList:
					self._delList.append(handler)
		else:
			self._handlerList.remove(handler)
		if self._usageCB \
		and len(self._handlerList) == len(self._delList):
			self._usageCB(self._name, 0)

	def activate(self, triggerData):
		if self._blocked:
			self._needActivate = 1
			# don't raise trigger multiple times for identical
			# data
			if id(triggerData) not in self._needActivateMap:
				self._needActivateMap[id(triggerData)] = True
				self._needActivateData.append(triggerData)
			return
		locked = self._locked
		self._locked = 1
		from chimera import APPQUIT
		prederegister = self._name == APPQUIT
		for handler in self._handlerList:
			if handler in self._delList:
				continue
			if prederegister:
				self._delList.append(handler)
			try:
				ret = handler.invoke(self._name, triggerData)
			except:
				self._locked = locked
				raise
			if ret == ONESHOT and handler not in self._delList:
				self._delList.append(handler)
		self._locked = locked
		if not self._locked:
			for handler in self._delList:
				self._handlerList.remove(handler)
			self._delList = []
			self._handlerList = self._addList + self._handlerList
			self._addList = []

	def block(self):
		self._blocked = self._blocked + 1

	def release(self):
		if self._blocked <= 0:
			raise StandardError, "more releases than blocks"
		self._blocked = self._blocked - 1
		if not self._needActivate or self._blocked:
			return
		self._needActivate = 0
		for activateData in self._needActivateData:
			self.activate(activateData)
		self._needActivateData = []
		self._needActivateMap.clear()

	def numHandlers(self):
		return len(self._handlerList) + len(self._addList) - len(self._delList)

class TriggerSet:
	"""Keep track of related groups of triggers."""

	def __init__(self):
		self._triggerDict = {}

	def addTrigger(self, name, usageCB=None):
		"""Add a trigger with the given name.

		triggerset.addTrigger(name) => None

		The name should be a string.  If a trigger by the same name
		already exists, an exception is raised.

		The optional 'usageCB' argument can be used to provide a
		callback function for when the trigger goes from no handlers
		registered to at least one registered, and vice versa.
		The callback function will be given the trigger name and 1
		or 0 (respectively) as arguments.
		"""
		if name in self._triggerDict:
			raise KeyError, name
		self._triggerDict[name] = _Trigger(name, usageCB)

	def deleteTrigger(self, name):
		"""Remove a trigger with the given name.

		triggerset.deleteTrigger(name) => None

		The name should be a string.  If no trigger corresponds to
		the name, an exception is raised.
		"""
		del self._triggerDict[name]

	def activateTrigger(self, name, data, absentOkay=False):
		"""Invoke all handlers registered with the given name.

		triggerset.activateTrigger(name, data) => None

		If no trigger corresponds to name, an exception is raised.
		Handlers are invoked in the order in which they were
		registered, and are called in the following manner: 

		function(name, userData, data) 

		where function and userData are the objects registered with
		addHandler, name is the name of the trigger, and triggerData
		is the last argument to the activateTrigger() call.

		During trigger activation, Handlers may add new handlers or
		delete existing handlers.  These operations, however, are
		deferred until after all handlers have been invoked; in
		particular, for the current trigger activation, newly added
		handlers will not be invoked and newly deleted handlers will
		be invoked.
		"""
		if name not in self._triggerDict:
			if absentOkay:
				return
			raise KeyError, name
		self._triggerDict[name].activate(data)

	def blockTrigger(self, name):
		"""Block all handlers registered with the given name.

		triggerset.blockTrigger(name) => None

		If no trigger corresponds to name, an exception is raised.
		blockTrigger()/releaseTrigger() may be nested inside other
		blockTrigger()/releaseTrigger() pairs.
		"""
		self._triggerDict[name].block()

	def releaseTrigger(self, name):
		"""Release all handlers registered with the given name.

		triggerset.releaseTrigger(name) => None

		If no trigger corresponds to name, an exception is raised.
		The last call to activateTrigger() made between the outermost
		blockTrigger()/releaseTrigger() pair is executed.
		"""
		self._triggerDict[name].release()

	def hasTrigger(self, name):
		return name in self._triggerDict

	def addHandler(self, name, func, data):
		"""Register a handler with the trigger with the given name.

		triggerset.addHandler(name, func, data) => handler

		If no trigger corresponds to name, an exception is raised.
		A handler consists of a callable object, function, and an
		arbitrary object, argument.  addHandler returns a handler
		identifying the handler for use with deleteHandler. 
		"""
		if name not in self._triggerDict:
			raise KeyError, name
		handler = _TriggerHandler(func, data)
		self._triggerDict[name].add(handler)
		return handler

	def deleteHandler(self, name, handler):
		"""Deregister the handler from the trigger with the given name.

		triggerset.deleteHandler(name, handler) => None

		The handler should be the return value from a previous call
		to addHandler.  If no trigger corresponds to name or no handler
		with the given handler is registered, an exception is raised.
		"""
		self._triggerDict[name].delete(handler)

	def hasHandlers(self, name):
		"""Return if the trigger with the given name has any handlers.

		triggerset.hasHandlers(name) => bool

		If no trigger corresponds to name, an exception is raised.
		"""
		return self._triggerDict[name].numHandlers() != 0
