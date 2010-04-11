# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:		DelPhiExecutor.py
Date:		06.08.2000
Description:	Handles the execution of a DelPhi run.

Imports:	- tempfile module

Classes:	DelPhiExecutor
	Input:	- DelPhi input options
		- DelPhi parameters
		- DelPhi output options
	Output:	- DelPhi (redirected) output file
		- specified by DelPhi output options

Caveats:

Last modified:	06.19.2000 - Cleaned up the DelPhiExecutor constructor
				and some comments and print statements
		07.01.2000 - Mucked around with the forking and Legacy
				code with dek.
		07.11.2000 - Tested the temporary worker thread class.
		12.12.2006 - Get executable file name from options.
"""

# general modules 
import os, os.path
import re

from chimera import replyobj

# temporary worker thread class
from ThreadProcess import WorkerThread
from DelPhiGlobals import OutputFileOption, MoleculeInputOption
from DelPhiGlobals import InputFileOption, ExecFileOption
import Tkinter

# Delphi on Windows has the limitation that file names in
# the parameter file cannot contain whitespace or "~".
# Unfortunately, this basically prevents any reference to
# places such as "c:\Program Files\..." and
# "c:\Documents and Settings\...".  In particular,
# if the user wants the output file in one of these
# inaccessible locations, we would have to copy a
# potentially large file.  Our workaround is to
# create a temporary directory in the output file
# directory, and copy all referenced files into there.
# Before we run Delphi, we change to the output file
# directory, so all the filename that appear in the
# parameter file will not have "illegal" characters.

class DelPhiExecutor:
	
	IllegalChars = re.compile("[^"
			"ABCDEFGHIJKLMNOPQRSTUVWZYZ.:_\-+=!@#$^123"
			"4567890abcdefghijklmnopqrstuvwxyz|\/?><;"
			"]")

	def __init__(self, options=None, outputFileName='delphi.out'):

		# initialize the base class
		#print self, "Initializing DelPhiExecutor..."
		self.options = options	
		self.outputFileName = outputFileName
		self.prmFileName = None
		self.phiFileName = None
		self.pdbFileName = None
		self.siteOutputFileName = None
		self.siteInputFileName = None
		self.process = None
		#print self, "Initialized."

	def __call__(self):
		self.noError = True
		self.executable = None
		self.FindOutputDir()
		self.WriteInput()
		self.CopyMappedInput()
		self.RunCommand()
		return self

	def FindOutputDir(self):
		dir = None
		for a, optionsgroup in self.options:
			for b, optionslist in optionsgroup:
				for o in optionslist:
					if not isinstance(o, OutputFileOption):
						continue
					if o.statement == "phi":
						name = o.var.get()
						if os.path.isabs(name):
							dir = os.path.dirname(name)
						else:
							dir = os.getcwd()
		if dir is None:
			replyobj.error('No PHI file was specified\n')
		self.outputDir = dir

	def WriteInput(self):
		# write the DelPhi options to a temporary file
		#print self, "Writing input file..."
		import tempfile
		self.inputFileMap = {}
		self.outputFileMap = {}
		fd, self.prmFileName = tempfile.mkstemp(dir=self.outputDir)
		os.close(fd)
		prmfile = open(self.prmFileName, 'w')
		for a, optionsgroup in self.options:
			for b, optionslist in optionsgroup:
				for option in optionslist:
					self.writeOption(prmfile, option)
		if self.siteOutputFileName and not self.siteInputFileName:
			prmfile.write("in(frc, file=\"%s\"\n" % self.pdbFileName)
		prmfile.close()
		#print self, "Input file written."

	def writeOption(self, f, o):
		# Split filemap into input and output for
		# copying before and after execution
		kw = {}
		if isinstance(o, OutputFileOption):
			if o.statement == 'log':
				filename = o.var.get()
				if filename:
					self.outputFileName = filename
				return
			filename = self.mapFileName(o, self.outputFileMap, kw)
			if o.statement == 'phi':
				self.phiFileName = filename
			elif o.statement == 'frc':
				self.siteOutputFileName = filename
		elif isinstance(o, MoleculeInputOption):
			self.pdbFileName = self.mapFileName(o,
							self.inputFileMap, kw)
		elif isinstance(o, ExecFileOption):
			self.executable = o.var.get()
			return
		elif isinstance(o, InputFileOption):
			if o.statement == 'frc':
				self.siteInputFileName = o.var.get()
			self.mapFileName(o, self.inputFileMap, kw)
		o.delPhiStatement(f, **kw)

	def mapFileName(self, opt, fileMap, kw):
		if not opt.var:
			return None
		filename = opt.var.get()
		if not filename:
			return None
		if not self.IllegalChars.search(filename):
			if not os.path.isabs(filename):
				filename = os.path.abspath(filename)
				kw["filename"] = filename
			return filename
		import tempfile
		fd, tempName = tempfile.mkstemp(dir=self.outputDir)
		os.close(fd)
		fileMap[tempName] = filename
		kw["filename"] = os.path.basename(tempName)
		return tempName

	def CopyMappedInput(self):
		# Copy any input file whose name was mapped
		for dst, src in self.inputFileMap.iteritems():
			fi = open(src, "rb")
			fo = open(dst, "wb")
			fo.write(fi.read())
			fi.close()
			fo.close()

	def RunCommand(self):
		cmd = "\"%s\" %s > %s" % (self.executable, self.prmFileName,
						self.outputFileName)
		#print self, "Running command:", `cmd`
		#print self, "Output dir:", `self.outputDir`
		self.process = WorkerThread(cmd, self.outputDir)
		self.process.run()
		#print self, "Done running command."

	def ShowOutput(self):
		proc = self.process
		print "--- DelPhi ---"
		proc = self.process
		if proc.stdoutData:
			print "--- Output ---"
			print proc.stdoutData
		if proc.stderrData:
			print "--- Errors ---"
			print proc.stderrData
		print ("--- Elapsed time = %d seconds ---" %
				(proc.endTime - proc.startTime))

	def CheckErrors(self):
		#print self, "Checking errors..."
		msgs = []
		if self.process.exitStatus != 0:
			msgs.append('Delphi exited with status %s\n'
					% str(self.process.exitStatus))
		if self.phiFileName:
			if not os.path.isfile(self.phiFileName):
				msgs.append('Output PHI file "%s" '
						'was not created\n'
							% self.phiFileName)
			self.phiFileName = None
		if msgs:
			self.noError = False
			replyobj.error(''.join(msgs))
		#print self, "Errors checked."

	def CopyMappedOutput(self):
		# Copy any output file whose name was mapped
		for src, dst in self.outputFileMap.iteritems():
			try:
				os.rename(src, dst)
			except os.error:
				fi = open(src, "rb")
				fo = open(dst, "wb")
				fo.write(fi.read())
				fi.close()
				fo.close()

	def Cleanup(self):
		#print self, "Cleaning up..."
		f = open(self.prmFileName)
		print f.read()
		f.close()
		try:
			os.remove(self.prmFileName)
		except os.error:
			pass
		for junk in self.outputFileMap.iterkeys():
			try:
				os.remove(junk)
			except os.error:
				pass
		for junk in self.inputFileMap.iterkeys():
			try:
				os.remove(junk)
			except os.error:
				pass
		#print self, "Cleaned up."

	def isRunning(self):
		if self.process:
			if self.process.isRunning():
				return 1
			self.ShowOutput()
			self.CheckErrors()
			self.CopyMappedOutput()
			self.Cleanup()
			self.process = None
		return 0

	def success(self):
		return self.noError

if __name__ == '__main__':
	d = DelPhiExecutor(None)
	d()

