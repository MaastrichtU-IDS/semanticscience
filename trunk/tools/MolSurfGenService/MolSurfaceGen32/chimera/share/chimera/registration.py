import httplib
import urllib
import string

import chimera
from chimera import replyobj
import string
import time

RegistrationFile = 'registration'
UsageFile = 'preregistration'

# FreeUsageDays is the numbers of days that an user can start
# Chimera without registration.
FreeUsageDays = 15

def checkRegistration(nag=1):
	"Check registration status."

	pf = chimera.pathFinder()
	filenames = pf.allExistingFiles('', RegistrationFile)
	if not filenames:
		if nag:
			return _checkUsage(pf)
		else:
			return
	import x509
	store = x509.CAStore()
	smime = x509.SMIME(store)
	for filename in filenames:
		try:
			text, signers = smime.verifyFile(filename)
		except x509.error, emsg:
			if emsg == 'Verify error:Certificate has expired':
				replyobj.warning('Registration file "%s" '
						'has expired.\n' % filename)
			continue
		valid = 0
		for cert in signers:
			fromUC = 0
			fromCGL = 0
			fields = string.split(cert.subject(), '/')
			for f in fields:
				if f == 'O=University of California, San Francisco':
					fromUC = 1
				elif f == 'OU=Computer Graphics Laboratory':
					fromCGL = 1
			if fromUC and fromCGL:
				valid = 1
				break
		if not valid:
			replyobj.warning('Registration file "%s" '
						'is not signed by CGL.\n'
						% filename)
		lines = string.split(text, '\r\n')
		param = {}
		for line in lines:
			try:
				key, value = map(string.strip,
							string.split(line, ':'))
			except ValueError:
				pass
			else:
				param[key] = value
		if param.has_key('Expires') \
		and time.time() > float(param['Expires']):
			replyobj.warning('Registration file "%s" '
						'has expired.\n' % filename)
		# Other parameter-dependent processing can go here
		return param

	if nag:
		return _checkUsage(pf)
	else:
		return

def _checkUsage(pf):
	"Check whether it's time to nag."

	t = time.localtime(time.time())
	thisUse = '%d-%d-%d' % (t[0], t[1], t[2])
	for filename in pf.allExistingFiles('', UsageFile):
		try:
			f = open(filename, 'rU')
		except IOError:
			continue
		param = {}
		while 1:
			line = f.readline()
			if not line:
				break
			try:
				key, value = map(string.strip,
							string.split(line, ':'))
			except ValueError:
				pass
			else:
				param[key] = value
		f.close()
		if not param.has_key('time') or not param.has_key('count'):
			continue
		lastUse = param['time']
		usageCount = int(param['count'])
		if thisUse != lastUse:
			usageCount = usageCount + 1
			_createUsage(pf, thisUse, usageCount, prefer=filename)
		if usageCount < FreeUsageDays:
			return None

		from baseDialog import ModelessDialog
		import Tkinter
		class RegisterDialog(ModelessDialog):
			title = "Registration Reminder"
			buttons = ("Register", "Later")

			def __init__(self):
				ModelessDialog.__init__(self, oneshot=1)

			def fillInUI(self, parent):
				l = Tkinter.Label(parent, text="You have used Chimera for %d days.\n"
						               "You can either register now by\n"
							       "clicking the 'Register' button below,\n"
						               "below or by selecting 'Registration..'\n"
						               "from the Help menu at any time.\n"
						               "\n"
						               "Registration is free and is only used for\n"
						               "reporting summary statistics to the NIH.\n"
						               % usageCount)
				l.grid(row=0, column=0, sticky="nsew")
				parent.rowconfigure(0,weight=1)
				parent.columnconfigure(0, weight=1)

			def Register(self):
				from chimera import dialogs, register
				dialogs.display(register.RegDialog.name)
				self.Cancel()
			def Later(self):
				self.Cancel()
		if chimera.nogui:
			import sys
			sys.stderr.write("You have used an unregistered copy of Chimera for %d days.\n"
					 "You can either register now by visiting:\n"
					 "   http://www.cgl.ucsf.edu/cgi-bin/chimera_registration.py\n"
					 "\nOr by choosing 'Registration' from the 'Help' menu next time "
					 "you start Chimera with the gui enabled.\n"
					 "Registration is free and is only used for reporting summary statistics "
					 "to the NIH.\n" % usageCount)
		else:
			RegisterDialog()			     

		return None
	_createUsage(pf, thisUse, 1)
	return None

def _openFile(pf, filename):
	"Open a (pre)registration file for writing."

	# Try creating .chimera in the home directory
	try:
		import os
		os.makedirs(pf.pathList('', '', 0, 0, 1)[0])
	except (IndexError, OSError):
		pass

	filenames = pf.pathList('', filename, 0, 1, 1)
	filenames.reverse()
	for path in filenames:
		try:
			f = open(path, 'w')
		except IOError:
			continue
		return f, path
	return None, None

def _createUsage(pf, thisUse, usageCount, prefer=None):
	"Create a new preregistration usage file."

	f = None
	if prefer:
		try:
			f = open(prefer, 'w')
		except IOError:
			f = None
	if not f:
		f, path = _openFile(pf, UsageFile)
	if f:
		f.write('time: %s\n' % thisUse)
		f.write('count: %d\n' % usageCount)
		f.close()

def install(msg):
	import x509
	store = x509.CAStore()
	smime = x509.SMIME(store)
	try:
		text, signers = smime.verifyString(msg, 0, len(msg))
	except x509.error, s:
		errormsg ='Registration message cannot be verified: %s.' % s 
		#print errormsg
		return (0,errormsg)
	pf = chimera.pathFinder()
	f, path = _openFile(pf, RegistrationFile)
	if not f:
		errormsg = 'Cannot find a writable file for registration message.'
		#print errormsg
		return (0,errormsg)
	f.write(msg)
	f.close()
	#print 'Registration message installed in "%s".' % path
	return (1,'Registration message installed in "%s".' % path)

#def register(user, organization, email):
#	conn = httplib.HTTP('www.cgl.ucsf.edu', 16160)
#	conn.putrequest('POST', '/cgi-bin/chimera_registration.py')
#	dataList = [ combine('user', user), ]
#	if organization:
#		dataList.append(combine('organization', organization))
#	if email:
#		dataList.append(combine('email', email))
#	request = string.join(dataList, '&')
#	conn.putheader('Content-Type', 'application/x-www-form-urlencoded')
#	conn.putheader('Content-Length', str(len(request)))
#	conn.endheaders()
#	conn.send(request)
#	code, msg, headers = conn.getreply()
#	if code != 200:
#		raise IOError, msg
#	f = conn.getfile()
#	reply = f.read()
#	f.close()
#	print reply
#	
#def combine(key, value):
#	return '%s=%s' % (key, urllib.quote_plus(value))	
