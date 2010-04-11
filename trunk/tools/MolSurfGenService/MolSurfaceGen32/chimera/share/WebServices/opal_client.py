#!/usr/local/bin/python2.5

class OpalService:

	def __init__(self, serviceName=None,
		opalURL="http://webservices.rbvi.ucsf.edu/opal/services/",
		sessionData=None):

		from AppService_client import AppServiceLocator
		from AppService_client import getAppMetadataRequest
		self.busy = False
		self.appLocator = AppServiceLocator()
		if sessionData:
			self.serviceURL, self.jobID, self.status = sessionData
			try:
				from cPickle import loads
			except ImportError:
				from pickle import loads
		else:
			self.serviceURL = opalURL + serviceName
			self.jobID = None
			self.status = None
		self.appServicePort = self.appLocator.getAppServicePort(
							self.serviceURL)
		if not sessionData:
			req = getAppMetadataRequest()
			resp = self.appServicePort.getAppMetadata(req)
			#print resp._usage

	def sessionData(self):
		return self.serviceURL, self.jobID, self.status

	def _saveStatus(self, status):
		self.status = (status._code, status._message, status._baseURL)

	def currentStatus(self):
		if self.status:
			return self.status[1]
		elif self.busy:
			return "waiting for response from Opal server"
		else:
			return "no Opal job running"

	def launchJob(self, cmdLine, **kw):
		if self.jobID is not None or self.busy:
			raise RuntimeError("Job has been launched already")
		import chimera
		from AppService_client import launchJobRequest
		import socket
		req = launchJobRequest()
		req._argList = cmdLine
		for key, value in kw.iteritems():
			setattr(req, key, value)
		if chimera.nogui:
			try:
				resp = self.appServicePort.launchJob(req)
			except socket.error, e:
				from chimera import NonChimeraError
				raise NonChimeraError(str(e))
			self.jobID = resp._jobID
			self._saveStatus(resp._status)
		else:
			from chimera.tkgui import runThread
			self.busy = True
			#import sys
			#print >> sys.__stderr__, "calling launchJobInThread"
			runThread(self._launchJobInThread, req)

	def _launchJobInThread(self, q, req):
		#import sys
		#print >> sys.__stderr__, "executing launchJobInThread"
		try:
			resp = self.appServicePort.launchJob(req)
		except socket.error, e:
			from chimera import NonChimeraError
			q.put(self._raiseError, NonChimeraError, str(e))
		else:
			self.jobID = resp._jobID
			self._saveStatus(resp._status)
		self.busy = False
		q.put(q)
		#import sys
		#print >> sys.__stderr__, "returning from launchJobInThread"

	def _raiseError(self, eClass, eMsg):
		raise eClass(eMsg)

	def launchJobBlocking(self, cmdLine, **kw):
		if self.jobID is not None:
			raise RuntimeError("Job has been launched already")
		from AppService_client import launchJobBlockingRequest
		import socket
		req = launchJobBlockingRequest()
		req._argList = cmdLine
		for key, value in kw.iteritems():
			setattr(req, key, value)
		try:
			resp = self.appServicePort.launchJobBlocking(req)
		except socket.error, e:
			from chimera import NonChimeraError
			raise NonChimeraError(str(e))
		self._saveStatus(resp._status)
		try:
			fileMap = self._makeOutputs(resp._jobOut)
		except:
			fileMap = None
		return (resp._status._code == 8, fileMap)

	def showStatus(self):
		print "Status:"
		code, message, baseURL = self.status
		print "\tCode:", code
		print "\tMessage:", message
		print "\tOutput Base URL:", baseURL

	def isFinished(self):
		#import sys
		#print >> sys.__stderr__, "executing isFinished", self.busy
		if self.busy:
			#print >> sys.__stderr__, "busy"
			return 0
		if self.status is None:
			#print >> sys.__stderr__, "no job"
			return 1
		code = self.status[0]
		if code == 8:
			# Normal finish
			#print >> sys.__stderr__, "normal"
			return 1
		elif code == 4:
			# Abnormal finish
			#print >> sys.__stderr__, "abnormal"
			return -1
		else:
			# Not finished
			#print >> sys.__stderr__, "not finished"
			return 0

	def queryStatus(self):
		#import sys
		#print >> sys.__stderr__, "calling from queryStatus", self.busy
		if self.busy:
			return
		if self.status is None:
			raise RuntimeError("No job has been launched yet")
		import chimera
		from AppService_client import queryStatusRequest
		import socket
		req = queryStatusRequest(self.jobID)
		if chimera.nogui:
			try:
				status = self.appServicePort.queryStatus(req)
			except socket.error, e:
				from chimera import NonChimeraError
				raise NonChimeraError(str(e))
			self._saveStatus(status)
		else:
			from chimera.tkgui import runThread
			self.busy = True
			#import sys
			#print >> sys.__stderr__, "calling from queryStatusInThread"
			runThread(self._queryStatusInThread, req)

	def _queryStatusInThread(self, q, req):
		#import sys
		#print >> sys.__stderr__, "executing from queryStatusInThread"
		try:
			status = self.appServicePort.queryStatus(req)
		except socket.error, e:
			from chimera import NonChimeraError
			q.put(self._raiseError, NonChimeraError, str(e))
		else:
			self._saveStatus(status)
		self.busy = False
		q.put(q)
		#import sys
		#print >> sys.__stderr__, "returning from queryStatusInThread"

	def getOutputs(self):
		if self.status is None:
			raise RuntimeError("No job has been launched yet")
		from AppService_client import getOutputsRequest
		import socket
		req = getOutputsRequest(self.jobID)
		try:
			resp = self.appServicePort.getOutputs(req)
		except socket.error, e:
			from chimera import NonChimeraError
			raise NonChimeraError(str(e))
		return self._makeOutputs(resp)

	def _makeOutputs(self, out):
		fileMap = {
			"stdout.txt": out._stdOut,
			"stderr.txt": out._stdErr,
		}
		for file in out._outputFile:
			fileMap[file._name] = file._url
		return fileMap

	def destroy(self):
		if self.jobID is None:
			self.status = None
			return
		from AppService_client import destroyRequest
		import socket
		req = destroyRequest(self.jobID)
		try:
			status = self.appServicePort.destroy(req)
		except socket.error, e:
			from chimera import NonChimeraError
			raise NonChimeraError(str(e))
		#self.status = self._saveStatus(status)
		#self.showStatus()
		# Mark that no jobs are running
		self.status = None
		self.jobID = None

def makeInputFile(path, name=None):
	from AppService_types import ns0
	inputFile = ns0.InputFileType_Def("inputFile")
	if name is None:
		import os.path
		name = os.path.basename(path)
	inputFile._name = name
	f = open(path)
	inputFile._contents = f.read()
	f.close()
	return inputFile

if __name__ == "__main__":
	def launchJobTest(opal, argList, **kw):
		import time, sys
		opal.launchJob(argList, **kw)
		while not opal.isFinished():
			opal.showStatus()
			sys.stdout.flush()
			time.sleep(10)
			opal.queryStatus()
		opal.showStatus()
		success = opal.isFinished() > 0
		fileMap = opal.getOutputs()
		return success, fileMap

	if 0:
		import pprint
		# Test pdb2pqr at NBCR
		service = "Pdb2pqrOpalService"
		NBCR_Opal = "http://ws.nbcr.net:8080/opal/services/"
		argList = "--ff=amber sample.pdb sample.pqr"
		inputFiles = [ makeInputFile("opal_testdata/sample.pdb") ]

		opal = OpalService(service, NBCR_Opal)

		print "Testing non-blocking job"
		success, fileMap = launchJobTest(opal, argList,
							_inputFile=inputFiles)
		print "Success", success
		print "Outputs:"
		pprint.pprint(fileMap)
		opal.destroy()
		print "Finished non-blocking job"

		print "Testing blocking job"
		success, fileMap = opal.launchJobBlocking(argList,
							_inputFile=inputFiles)
		print "Outputs:"
		pprint.pprint(fileMap)
		opal.destroy()
		print "Finished blocking job"

	if 1:
		import pprint
		service = "BlastpdbServicePort"
		argList = "-i blastpdb.in -o blastpdb.out -e 1e-10"
		inputFiles = [ makeInputFile("opal_testdata/blastpdb.in") ]
		print "Launching blastpdb job"
		opal = OpalService(service)
		success, fileMap = launchJobTest(opal, argList,
							_inputFile=inputFiles)
		print "Success", success
		print "Outputs:"
		pprint.pprint(fileMap)
		print "Finished blastpdb job"
		def showFile(name, url):
			import sys, urllib2
			print "%s:" % name
			print "-----"
			f = urllib2.urlopen(url)
			sys.stdout.write(f.read())
			f.close()
			print "-----"
		showFile("blastpdb.in", fileMap["blastpdb.in"])
		if success:
			showFile("blastpdb.out", fileMap["blastpdb.out"])
		else:
			showFile("stdout", fileMap["stdout"])
			showFile("stderr", fileMap["stderr"])
