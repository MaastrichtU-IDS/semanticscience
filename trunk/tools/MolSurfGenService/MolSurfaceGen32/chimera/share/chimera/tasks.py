#
# Task manager
#
# Tasks may be created with callbacks for status updates and
# cancellation.  Tasks may be either modal or non-modal.
# Internal (weak) references to tasks are kept so that we
# have a history of tasks started and completed.
#
# For modal tasks, we grab the input for the status line
# tasks button.  The task is responsible for updating
# status and calling event handling routines.
#
# For non-modal tasks, if there is a status update callback, a
# "check for changes" handler is registered and the callback
# is invoked at the requested frequency (defined by the number
# of frames updates between checks).
#
# Status updates for a task should be sent via the task instance
# method rather than directly to the status line.  This way, when
# multiple tasks are active, the latest status for each may be
# shown separately.
#
# If there are more than one task registered, the status line is
# reconfigured to display a "show tasks" button that will bring
# up a Tasks dialog showing all active tasks.  If there are
# no tasks registered, then the button is hidden.  If there is
# one task running and there is no cancel callback, the button
# is displayed in red and disabled; if there is a cancel callback
# the button is displayed in green and enabled.
#
_manager = None

CFC = "check for changes"

def manager():
	global _manager
	if _manager is None:
		_manager = Manager()
	return _manager

defaultCancelCB = 'raiseCancelOperation'

class Task:
	"""Instance representing active tasks of one operation
	or a sequence of operations that may be canceled."""

	DefaultFrequency = (
		# updates are tied to check-for-changes triggers
		# which are fired about 30 times per second.
		( 60,	30 ),		# once per second for 60x
		( 4,	30 * 60 ),	# once per minute for 4x
		( 0,	30 * 60	* 5 ),	# once per 5 minutes thereafter
	)

	def __init__(self, title, cancelCB=defaultCancelCB,
			statusCB=None, statusFreq=None, modal=False):
		self.title = title
		self.cancelCBList = []
		self.raiseCancelOperation = (cancelCB is defaultCancelCB)
		if cancelCB and cancelCB is not defaultCancelCB:
			self.cancelCBList.append(cancelCB)
		self.statusCBList = []
		if statusCB:
			self.statusCBList.append(statusCB)
		self.statusCounter = 0
		if statusFreq is None:
			self.statusFreq = self.DefaultFrequency
		else:
			self.statusFreq = statusFreq
		self.modal = modal
		self.canceling = False
		self._internalTask = None	# set by registration
		manager()._registerTask(self)

	def addCallbacks(self, cancelCB, statusCB):
		if cancelCB:
			self.cancelCBList.insert(0, cancelCB)
		if statusCB:
			self.statusCBList.insert(0, statusCB)
		manager()._reregisterTask(self._internalTask)

	def removeCallbacks(self, cancelCB, statusCB):
		self.cancelCBList.remove(cancelCB)
		self.statusCBList.remove(statusCB)
		manager()._reregisterTask(self._internalTask)

	def runStatusCB(self, counter):
		curPeriod = 30
		for repeat, period in self.statusFreq:
			curPeriod = period
			interval = repeat * period
			if counter <= interval:
				break
			counter -= interval
		if counter % curPeriod > 0:
			return
		if self.statusCBList:
			self.statusCBList[0]()

	def runCancelCB(self):
		for cb in self.cancelCBList:
			cb()

	def status(self):
		"""Current status of task (as a string)"""
		if self.canceling:
			return "%s: canceling" % self.title
		else:
			return "%s: %s" % (self.title,
						self._internalTask.status)

	def updateStatus(self, newStatus):
		"""Set current status of task"""
		if self.canceling and self.raiseCancelOperation:
			self.raiseCancelOperation = False
			import chimera
			raise chimera.CancelOperation
		self._internalTask.updateStatus(newStatus)
		manager().statusUpdated(self)

	def finished(self):
		iTask = self._internalTask
		if iTask:
			iTask._deregister()
		

class _InternalTask:
	"""Instance representing either active or completed task."""

	def __init__(self, task):
		import weakref, time
		self.task = weakref.ref(task, self._deregister)
		self.title = task.title
		self.modal = task.modal
		self.startTime = time.time()
		self.endTime = None
		self.status = "<no update>"
		self.canceled = False

	def cancel(self):
		task = self.task()
		if task is not None and (task.cancelCBList or
					 task.raiseCancelOperation):
			self.canceled = True
			task.canceling = True
			self._deregister()
			task.runCancelCB()

	def updateStatus(self, newStatus):
		self.status = newStatus.strip()

	def _deregister(self, taskref = None):
		if self.endTime is None:
			import time
			self.endTime = time.time()
			manager()._deregisteredTask(self)


class Manager:
	"""Singleton for managing creation, destruction and display
	of active and completed tasks."""

	def __init__(self):
		from weakref import WeakKeyDictionary, WeakValueDictionary
		self._cfcHandler = None		# "check for changes" handler
		self._iTasks = []		# internal tasks in order
						#   of arrival
		self._modalTasks = []
		self.statusUpdateInterval = 0.5	# seconds between status updates
		self.nextStatusTime = 0

	#
	# Task registration and deregistration
	#
	def _registerTask(self, task):
		iTask = _InternalTask(task)
		self._iTasks.append(iTask)
		if iTask.modal:
			self._modalTasks.append(iTask)
		task._internalTask = iTask
		import dialogs
		d = dialogs.find(TaskPanel.name, create=False)
		if d:
			d.refreshTaskList()
			d.refreshCancelButtons()
		import statusline
		sl = statusline.status_line(create=False)
		if sl:
			sl.update_task_buttons()
		if iTask.modal:
			# If this task is modal, grab the input
			# for the status line tasks button
			if sl:
				sl.grab_task_button(True)
		else:
			# If this is the first one to have status
			# updates, then we need to register a "check for
			# changes" handler
			if not self._cfcHandler and self._statusCount() == 1:
				import chimera
				self._cfcHandler = chimera.triggers.addHandler(
						CFC, self._statusUpdateCB, None)
		import chimera
		if not chimera.nogui:
			from chimera import tkgui
			tkgui.update_windows()

	def _reregisterTask(self, iTask):
		from chimera import dialogs
		d = dialogs.find(TaskPanel.name, create=False)
		if d:
			d.updateTaskStatus(iTask)
			d.refreshCancelButtons()
		import statusline
		sl = statusline.status_line(create=False)
		if sl:
			sl.update_task_buttons()
		if not iTask.modal:
			# If this is the first one to have status
			# updates, then we need to register a "check for
			# changes" handler
			if not self._cfcHandler and self._statusCount() == 1:
				import chimera
				self._cfcHandler = chimera.triggers.addHandler(
						CFC, self._statusUpdateCB, None)
			elif self._cfcHandler and self._statusCount() == 0:
				import chimera
				chimera.triggers.deleteHandler(CFC,
						self._cfcHandler)
				self._cfcHandler = None
		import chimera
		if not chimera.nogui:
			from chimera import tkgui
			tkgui.update_windows()

	def _deregisteredTask(self, iTask):
		# This is called after the user task instance has been
		# disposed of.
		from chimera import replyobj
		if iTask.modal:
			self._modalTasks.remove(iTask)
		if iTask.canceled:
			msg = "canceled"
		else:
			msg = "finished"
		replyobj.status("%s: %s\n" % (iTask.title, msg), blankAfter=10)
		import statusline
		sl = statusline.status_line(create=False)
		if iTask.modal:
			# Terminate the input grab
			if sl:
				sl.grab_task_button(False)
		else:
			# If there are no more tasks with status updates,
			# deregister our "check for changed" handler
			if self._cfcHandler and self._statusCount() == 0:
				import chimera
				chimera.triggers.deleteHandler(CFC,
						self._cfcHandler)
				self._cfcHandler = None
		if sl:
			sl.update_task_buttons()
		from chimera import dialogs
		d = dialogs.find(TaskPanel.name, create=False)
		if d:
			d.updateTaskStatus(iTask)
			d.refreshCancelButtons()

	def _debugRefcount(self):
		import sys
		for iTask in self._iTasks:
			task = iTask.task()
			if task is not None:
				print " ", task, sys.getrefcount(task)

	def _statusCount(self):
		# Return the number of tasks that have status update callbacks
		count = 0
		for iTask in self._iTasks:
			task = iTask.task()
			if task is not None and task.statusCBList:
				count += 1
		return count

	def _statusUpdateCB(self, trigger, ignore, changes):
		# Call the status update callback at requested frequency
		for iTask in self._iTasks:
			task = iTask.task()
			if task is None or not task.statusCBList:
				continue
			import sys
			task.statusCounter += 1
			task.runStatusCB(task.statusCounter)

	# 
	# Callback functions invoked when task status changes
	#
	def statusUpdated(self, task):
		from time import time
		t = time()
		if t < self.nextStatusTime:
			return
		self.nextStatusTime = t + self.statusUpdateInterval
		# Status message for task was updated
		from chimera import replyobj
		# TODO: delay update to avoid overwhelming user
		replyobj.status("%s\n" % task.status())
		from chimera import dialogs
		d = dialogs.find(TaskPanel.name, create=False)
		if d:
			d.updateTaskStatus(task._internalTask)
		import chimera
		if not chimera.nogui:
			from chimera import tkgui
			tkgui.update_windows()

	def removeFinished(self):
		# Remove completed tasks from internal tasks list
		self._iTasks = [ iTask for iTask in self._iTasks
					if iTask.endTime is None ]

	#
	# Callback functions invoked when status line display changes or
	# user presses button
	#
	def active_modal_task(self):
		try:
			return self._modalTasks[-1]
		except IndexError:
			return None

	def stop_active_task(self):
		# Status line button was pressed.  Stop the
		# most recent modal task.
		iTask = self.active_modal_task()
		if iTask:
			iTask.cancel()

	def active_task_count(self):
		count = 0
		for iTask in self._iTasks:
			task = iTask.task()
			if task is not None:
				count += 1
		return count

	#
	# Interface used by Task Panel to display and cancel tasks
	#
	def internalTaskList(self):
		return self._iTasks

	def canCancelFromPanel(self, iTask):
		# Only active non-modal tasks can be canceled from Tasks panel
		# Active modal tasks can only be canceled from the stop
		# button on the status line since they grab the mouse
		task = iTask.task()
		if task is None:
			return False
		return task.cancelCBList


from baseDialog import ModelessDialog
class TaskPanel(ModelessDialog):
	title="Task Panel"
	buttons=("Close", "Clear Finished")
#	buttons=("Close", "Clear Finished", "Test", "Test Modal")
	name="task panel"
	help="UsersGuide/taskpanel.html"

	Columns = (
		(	"Status",	50	),
		(	"Started",	16	),
		(	"Run Time",	8	),
		(	"State",	8	),
	)
	N_STATUS = 0
	N_STARTED = 1
	N_RUNTIME = 2
	N_STATE = 3

	def fillInUI(self, parent):
		#
		# Set up some Tkinter options that will be used
		# for constructing widgets later
		#
		import tkgui
		self._widgetOpts = { "padx":3 } 
		if tkgui.windowSystem == 'aqua':
			self._widgetOpts["padx"] = 8
		self._gridOpts = { "sticky":"nsew" }
		self._titleOpts = self._widgetOpts.copy()
		self._titleOpts["relief"] = "flat"
		self.altBg, self.disabledColor = alternateColors(parent)

		from CGLtk.Table import ScrolledTable
		tt = ScrolledTable(parent)
		for n, (title, width) in enumerate(self.Columns):
			tt.setColumnTitle(n, title, width=width,
						**self._titleOpts)
		tt.pack(fill="both", expand=True)
		self.taskTable = tt
		self._widgets = {}
		self.refreshTaskList()

		# DEBUG:
		self.procList = []
		self.modalProcList = []

	def refreshTaskList(self):
		"""Refresh task list and redisplay"""
		import Tkinter, time
		mgr = manager()
		tt = self.taskTable
		n = 0
		f = tt.interior()
		# wList looks like (index, wStatus, wStarted, wRuntime, wState)
		for wList in self._widgets.itervalues():
			for w in wList[1:]:
				w.destroy()
		widgets = {}
		for iTask in mgr.internalTaskList():
			self._widgetOpts["bg"] = self.altBg[n % 2]
			tt.setRowTitle(n, iTask.title, padx=2, relief="flat")
			started = time.strftime("%I:%M:%S%p",
					time.localtime(iTask.startTime))
			runtime = self.runTime(iTask)
			if iTask.endTime is not None:
				self._widgetOpts["fg"] = self.disabledColor
			wList = [ n ]
			l = Tkinter.Label(f, text=iTask.status,
					width=self.Columns[self.N_STATUS][1],
					**self._widgetOpts)
			l.grid(row=n, column=self.N_STATUS, **self._gridOpts)
			wList.append(l)
			l = Tkinter.Label(f, text=started,
					width=self.Columns[self.N_STARTED][1],
					**self._widgetOpts)
			l.grid(row=n, column=self.N_STARTED, **self._gridOpts)
			wList.append(l)
			l = Tkinter.Label(f, text=runtime,
					width=self.Columns[self.N_RUNTIME][1],
					**self._widgetOpts)
			l.grid(row=n, column=self.N_RUNTIME, **self._gridOpts)
			wList.append(l)
			w = self.remakeStateWidget(f, iTask, n, None)
			wList.append(w)
			if iTask.endTime is not None:
				del self._widgetOpts["fg"]
			widgets[iTask] = wList
			n += 1
		while n < len(self._widgets):
			tt.setRowTitle(n, None)
			n += 1
		self._widgets = widgets
		tt.showTitles()

	def runTime(self, iTask):
		if iTask.endTime is None:
			runtime = "-"
		else:
			delta = iTask.endTime - iTask.startTime
			if delta < 60:
				runtime = "%d seconds" % delta
			else:
				delta = delta / 60.0
				if delta < 60:
					runtime = "%.1f minutes" % delta
				else:
					delta = delta / 60.0
					runtime = "%.1f hours" % delta
		return runtime

	def remakeStateWidget(self, f, iTask, n, oldWidget):
		import Tkinter
		self._widgetOpts["bg"] = self.altBg[n % 2]
		if iTask.endTime is None:
			mgr = manager()
			if mgr.canCancelFromPanel(iTask):
				widgetClass = Tkinter.Button
				state = "cancel"
				kw = self._widgetOpts.copy()
				kw["command"] = iTask.cancel
			else:
				widgetClass = Tkinter.Label
				state = "running"
				kw = self._widgetOpts
		else:
			widgetClass = Tkinter.Label
			if iTask.canceled:
				state = "canceled"
			else:
				state = "finished"
			kw = self._widgetOpts
		if isinstance(oldWidget, widgetClass):
			w = oldWidget
			w.config(text=state)
		else:
			w = widgetClass(f, text=state,
					width=self.Columns[self.N_STATE][1],
					**kw)
			w.grid(row=n, column=self.N_STATE, **self._gridOpts)
			if oldWidget:
				oldWidget.destroy()
		return w

	def updateTaskStatus(self, iTask):
		wList = self._widgets[iTask]
		# wList looks like (index, wStatus, wStarted, wRuntime, wState)
		wList[1].config(text=iTask.status)
		wList[3].config(text=self.runTime(iTask))
		wList[4] = self.remakeStateWidget(self.taskTable.interior(),
							iTask, wList[0],
							wList[4])
		if iTask.endTime is not None:
			for w in wList[1:]:
				w.config(fg=self.disabledColor)

	def refreshCancelButtons(self):
		mgr = manager()
		activeTask = mgr.active_modal_task()
		for iTask, wList in self._widgets.iteritems():
			if iTask.endTime != None:
				# Terminated tasks don't have cancel buttons
				continue
			if activeTask is None or activeTask is iTask:
				state = "normal"
			else:
				state = "disabled"
			wList[4].config(state=state)

	def modalCancelButton(self):
		mgr = manager()
		activeTask = mgr.active_modal_task()
		if activeTask is None:
			return None
		try:
			wList = self._widgets[activeTask]
		except KeyError:
			return None
		else:
			return wList[4]

	def ClearFinished(self):
		"""Remove completed tasks from displayed list"""
		manager().removeFinished()
		self.refreshTaskList()

	def Test(self):
		self.procList.append(TestProcess())

	def TestModal(self):
		self.modalProcList.append(TestModalProcess())

def alternateColors(parent):
	"Generate an alternate color to the default background color"
	import Tkinter
	from CGLtk.color import rgba2tk
	from CGLtk.color.ColorWell import _tkrgb2rgba
	w = Tkinter.Button(parent, text="Hello")
	bg = w.cget("bg")
	fg = w.cget("fg")
	disabledColor = w.cget("disabledforeground")
	b_r, b_g, b_b, b_a = _tkrgb2rgba(w.winfo_rgb(bg))
	f_r, f_g, f_b, f_a = _tkrgb2rgba(w.winfo_rgb(fg))
	w.destroy()
	r = b_r + (f_r - b_r) / 10.0
	g = b_g + (f_g - b_g) / 10.0
	b = b_b + (f_b - b_b) / 10.0
	alt_bg = rgba2tk((r, g, b, b_a))
	return (bg, alt_bg), disabledColor

import dialogs
dialogs.register(TaskPanel.name, TaskPanel)


#
# Code below are examples and not used by Chimera
#

class TestProcess:

	def __init__(self):
		self.checkCount = 0
		self.task = Task("test", self.cancelCB, self.statusCB)

	def cancelCB(self):
		self.finished()

	def statusCB(self):
		self.checkCount += 1
		if self.checkCount > 10:
			self.finished()
		else:
			self.task.updateStatus("count=%d" % self.checkCount)

	def finished(self):
		self.task = None


class TestModalProcess:

	def __init__(self):
		self.canceled = False
		self.task = Task("modal", self.cancelCB, modal=True)
		self.execute()

	def cancelCB(self):
		self.canceled = True

	def execute(self):
		import time
		from chimera import tkgui
		loopCount = 0
		while not self.canceled:
			time.sleep(1)
			self.task.updateStatus("loop=%d" % loopCount)
			tkgui.app.update()
			# Do the real work here
			loopCount += 1
			if loopCount >= 10:
				break
		self.task = None
