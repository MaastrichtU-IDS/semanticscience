from baseDialog import ModelessDialog

def registerIdType(dbname, width, example, cb, homepage, infourl,
		   search = None):
        info = (dbname, width, example, cb, homepage, infourl, search)
        global _fetchInfo
        _fetchInfo.append(info)
        d = fetchDialog(create = False)
	if d:
		d.addIdGui(info)
		d.fixWidgets()
        
_fetchDialog = None
def fetchDialog(create = True):
	global _fetchDialog
	if not _fetchDialog and create:
		_fetchDialog = _FetchDialog()
	return _fetchDialog

def showFetchDialog():
	fetchDialog().enter()

def fetchNDB(IDcode):
        fetchById(IDcode, 'NDB')

def fetchPDB(IDcode):
	fetchById(IDcode, "PDBID")

def fetchCIF(IDcode):
	fetchById(IDcode, "CIFID")

def fetchSCOP(IDcode):
	fetchById(IDcode, "SCOP")

def fetchById(IDcode, IDtype):
        import tkgui
	tkgui.openPath(IDcode, IDtype)

_fetchInfo = [
	("NDB", 6, "pde024", fetchNDB, "ndbserver.rutgers.edu",
	 "http://ndbserver.rutgers.edu/servlet/IDSearch.NDBSearch1?id=%s",
	 None),
	("PDB", 4, "1yti", fetchPDB, "www.rcsb.org/pdb/",
	 "http://www.rcsb.org/pdb/explore.do?structureId=%s", None),
	("PDB (mmCIF)", 4, "1yti", fetchCIF, "www.rcsb.org/pdb/",
	 "http://www.rcsb.org/pdb/explore.do?structureId=%s", None),
	("SCOP", 7, "d1g0sa_", fetchSCOP, "scop.berkeley.edu",
	 "http://scop.berkeley.edu/search.cgi?sid=%s", None)
]
		
class _FetchDialog(ModelessDialog):
	title = "Fetch Structure by ID"
	buttons = ("Fetch", "Web Page", "Close")
#	default = "Fetch"
	keepShown = "Fetch"
	help = "UsersGuide/fetch.html"

	def fillInUI(self, parent):
		self.parent = parent
		parent.columnconfigure(2, weight=1)
		self.prefCat = "main Chimera open panel"
		self.dbPref = "database"
                import preferences
		self.prefs = preferences.addCategory(self.prefCat,
						preferences.HiddenCategory,
						optDict={ self.dbPref: "PDB" })

                import Tkinter
		self.dbVar = Tkinter.StringVar(parent)
		self.dbVar.set(self.prefs[self.dbPref])

		for c, name  in enumerate(("Database", "ID", "Example")):
			h = Tkinter.Label(parent, text=name,
					  relief='groove', borderwidth=2)
			h.grid(row=0, column=c, sticky='ew')
		
		self.fetchEntries = []
		self.exampleLabels = []
		for info in _fetchInfo:
                        self.addIdGui(info)

                row = len(self.fetchEntries) + 1

		pb = Tkinter.Button(parent, text = 'Set download directory',
				    command = self.showPreferences)
		pb.grid(row = row, column = 0, columnspan = 3, sticky = 'e')
		row += 1

		sf = Tkinter.Frame(parent)
		sf.columnconfigure(0, weight = 1)
		sf.grid(row = row, column = 0, columnspan = 3, sticky = 'ew')
		self.searchFrame = sf
		row += 1
		sb = Tkinter.Button(sf, text = 'Search',
				    command = self.searchCB)
		self.searchButton = sb
		sb.grid(row = 0, column = 1, padx = 3, sticky = 'w')
		self.searchVar = Tkinter.StringVar(parent)
		se = Tkinter.Entry(sf, textvariable = self.searchVar)
		self.searchEntry = se
		se.grid(row = 0, column = 0, padx = 3, sticky = 'ew')
		se.bind('<Return>', self.searchCB)

		self.fixWidgets()	# Gray-out inactive widgets

	def map(self, e=None):
		# For some reason, which db entry has the focus is lost
		# when the Fetch dialog is brought up a second time, so
		# set focus to current db entry.
		db = self.dbVar.get()
		for i, info in enumerate(_fetchInfo):
			if info[0] == db:
				self.fetchEntries[i].focus_set()
				break

	def addIdGui(self, info):
		db, width, example, cb, homePage, infoURL, search = info
                row = len(self.fetchEntries) + 1
		import Tkinter
		Tkinter.Radiobutton(self.parent, command=self.fixWidgets,
			text=db, variable=self.dbVar, value=db
			).grid(row=row, column=0, sticky="w")
		e = Tkinter.Entry(self.parent, width=width)
		e.bind('<Return>', lambda e: self.Fetch())
		self.fetchEntries.append(e)
		self.exampleLabels.append(Tkinter.Label(self.parent,
						text=example))
		self.exampleLabels[-1].grid(row=row, column=2)

	# Display only id code entry field for selected id type.
	def fixWidgets(self):
		db = self.dbVar.get()
		for i, info in enumerate(_fetchInfo):
			if info[0] == db:
				self.fetchEntries[i].grid(row=i+1, column=1, padx=10)
				self.fetchEntries[i].focus_set()
				self.exampleLabels[i].configure(state="normal")
				sf = self.searchFrame
				if info[6]:
					sf.grid(row = len(self.fetchEntries)+2)
				else:
					sf.grid_remove()
			else:
				self.fetchEntries[i].grid_forget()
				self.exampleLabels[i].configure(
							state="disabled")

	def showPreferences(self):
		from chimera import dialogs
		d = dialogs.display('preferences')
		d.menu.invoke(index = FETCH_PREFERENCES)

	def searchCB(self, event = None):
		i = self.dbIndex()
		if i is None:
			return
		f = _fetchInfo[i]
		searchFunc = f[6]
		if searchFunc is None:
			return
		text = self.searchVar.get()
		if not text:
			return
		from chimera.replyobj import status
		status('Searching %s for "%s" ...' % (f[0], text))
		sb = self.searchButton
		sb.config(state = 'active')
		sb.update_idletasks()	# Change button appearance
		searchFunc(text)
		sb.config(state = 'normal')
		status('')
		
	def Apply(self):
		db = self.dbVar.get()
		self.prefs[self.dbPref] = db
		fetched = False
		i = self.dbIndex()
		if i != None:
			entry = self.fetchEntries[i]
			code = entry.get()
			entry.delete(0, 'end')
			if code:
				_fetchInfo[i][3](code)
				fetched = True
		if not fetched:
			self.enter()
			from chimera import replyobj
			replyobj.error("No %s ID entered\n" % db)

	def WebPage(self):
		self.showWebPage()

	def showWebPage(self):
		i = self.dbIndex()
		if i == None:
			code = ''
		else:
			code = self.fetchEntries[i].get()
		infoURL = _fetchInfo[i][5]
		if code and infoURL:
			url = infoURL % code
		else:
			homePage = _fetchInfo[i][4]
			url="http://" + homePage
		# use help module to centralize error recovery
		import help
		help.display(url)

	def dbIndex(self):
		db = self.dbVar.get()
		for i, info in enumerate(_fetchInfo):
			if info[0] == db:
				return i
		return None

# -----------------------------------------------------------------------------
# Download file from web.
#
def fetch_file(url, name, minimum_file_size = None, save_dir = '',
			save_name = '', uncompress = False, ignore_cache = False):
	"""a fetched non-local file that doesn't get cached will be
	   removed when Chimera exits

	   if 'ignore_cache' is True, then cached values will be ignored,
	   though the retrieved values will still be cached if appropriate
	"""

	from chimera.replyobj import status
	status('Fetching %s\n' % (name,))
	
	if save_name and not ignore_cache:
		path = fetch_local_file(save_dir, save_name)
		if path:
			return path, {}

	from chimera import tasks
	task = tasks.Task("Fetch %s" % name, modal=True)
	def report_cb(barrived, bsize, fsize):
		if fsize > 0:
			percent = min(100.0,(100.0*barrived*bsize)/fsize)
			prog = '%.0f%% of %s' % (percent, byte_text(fsize))
		else:
			prog = '%s received' % (byte_text(barrived*bsize),)
		task.updateStatus(prog)
	# TODO: In Python 2.5 socket.error is not an IOError, but in Python 2.6
	#       it is.  Remove socket error when Chimera uses Python 2.6.
	import urllib, socket
	try:
		path, headers = urllib.urlretrieve(url, reporthook = report_cb)
	except (IOError, socket.error), v:
		from chimera import NonChimeraError
		raise NonChimeraError('Error fetching %s: %s' % (name, str(v)))
	task.finished()		# Remove from tasks panel

	# Check if page is too small, indicating error return.
	if minimum_file_size != None:
		import os
		if os.stat(path).st_size < minimum_file_size:
			from chimera import NonChimeraError
			raise NonChimeraError('%s not available.' % name)

	if uncompress and path.endswith('.gz'):
		status('Uncompressing %s\n' % name)
		gunzip(path, path[:-3])
		status('\n')
		path = path[:-3]

	if save_name:
		spath = save_fetched_file(path, save_dir, save_name)
		if spath:
			path = spath
	if not (url.startswith("file:") or (save_name and spath)):
		from OpenSave import osTemporaryFile
		import os
		tmpPath = osTemporaryFile(suffix=os.path.splitext(path)[1])
		# Windows doesn't like rename to an existing file, so...
		if os.path.exists(tmpPath):
			os.unlink(tmpPath)
		import shutil
		shutil.move(path, tmpPath)
		path = tmpPath

	return path, headers

# -----------------------------------------------------------------------------
#
def byte_text(b):

	if b >= 1024*1024:
		return '%.1f Mbytes' % (float(b)/(1024*1024))
	elif b >= 1024:
		return '%.1f Kbytes' % (float(b)/1024)
	return '%d bytes' % int(b)

# -----------------------------------------------------------------------------
# Preferences for fetching files.
#
FETCH_PREFERENCES = 'Fetch'	# preferences category
FETCH_SAVE = 'Save fetched files'
FETCH_LOCAL = 'Use local files'
FETCH_DIRECTORY = 'Download directory'
from tkoptions import BooleanOption, OutputFileOption
class DirectoryOption(OutputFileOption):
	def __init__(self, *args, **kw):
		kw['title'] = 'Fetch by Id Download Directory'
		kw['dirsOnly'] = True
		OutputFileOption.__init__(self, *args, **kw)
fetchPreferences = {
	FETCH_SAVE: (BooleanOption, True, None),
	FETCH_LOCAL: (BooleanOption, True, None),
	FETCH_DIRECTORY: (DirectoryOption, '', None),
}
fetchPreferencesOrder = [FETCH_SAVE, FETCH_LOCAL, FETCH_DIRECTORY]
import preferences
preferences.register(FETCH_PREFERENCES, fetchPreferences)
preferences.setOrder(FETCH_PREFERENCES, fetchPreferencesOrder)

# -----------------------------------------------------------------------------
#
def fetch_local_file(save_dir, save_name):

	import preferences
	if not preferences.get(FETCH_PREFERENCES, FETCH_LOCAL):
		return None
	dir = preferences.get(FETCH_PREFERENCES, FETCH_DIRECTORY)
	if not dir:
		return None
	from os.path import join, isfile
	path = join(dir, save_dir, save_name)
	if not isfile(path):
		return None
	return path

# -----------------------------------------------------------------------------
#
def save_fetched_file(path, save_dir, save_name):

	spath = save_location(save_dir, save_name)
	if spath is None:
		return None
	from chimera import replyobj
	replyobj.status('Copying %s to download directory\n' % save_name)
	import shutil
	try:
		shutil.copyfile(path, spath)
	except IOError:
		return None
	replyobj.status('')
	return spath

# -----------------------------------------------------------------------------
#
def save_fetched_data(data, save_dir, save_name):

	spath = save_location(save_dir, save_name)
	if spath is None:
		return None
	from chimera import replyobj
	replyobj.status('Saving %s to download directory\n' % save_name)
	try:
		f = open(spath, 'wb')
		f.write(data)
		f.close()
	except IOError:
		return None
	replyobj.status('')
	return spath

# -----------------------------------------------------------------------------
#
def save_location(save_dir, save_name):

	import preferences
	if not preferences.get(FETCH_PREFERENCES, FETCH_SAVE):
		return None
	dir = preferences.get(FETCH_PREFERENCES, FETCH_DIRECTORY)
	from os.path import isdir, join, dirname
	if not dir or not isdir(dir):
		return None
	spath = join(dir, save_dir, save_name)
	sdir = dirname(spath)
	if not isdir(sdir):
		import os
		try:
			os.makedirs(sdir)
		except IOError:
			return None
	return spath

# -----------------------------------------------------------------------------
#
def gunzip(gzpath, path):

	import gzip
	gzf = gzip.open(gzpath)
	f = open(path, 'wb')
	f.write(gzf.read())
	f.close()
	gzf.close()
