def search_emdb(text):
        from WebServices.emdb_client import EMDB_WS
	ws = EMDB_WS()
	rt = ws.getResultSetXMLByTitle(text)
	ra = ws.getResultSetXMLByAuthor(text)
        ri = ws.getResultSetXMLByID(text)
        results = ws.rowValues(rt) + ws.rowValues(ra) + ws.rowValues(ri)
	# remove duplicates
	results = dict([(r['accessionCode'],r) for r in results]).values()
        if results:
                d = EMDBResultsDialog(results)
                d.enter()
	else:
		from chimera.replyobj import warning
		warning('No results for EMDB search "%s"' % text)
        return results

from chimera.baseDialog import ModelessDialog
class EMDBResultsDialog(ModelessDialog):
	buttons = ("Fetch Map", 'Fetch Map and PDBs', "Close")
	help = "UsersGuide/fetch.html"
	def __init__(self, emdb_entries):
		self.title = "EMDB Search Results"
                self.results = emdb_entries
		ModelessDialog.__init__(self)
		from chimera.extension import manager
		manager.registerInstance(self)

	def fillInUI(self, parent):
		top = parent.winfo_toplevel()
		row = 0

		from CGLtk.Table import SortableTable
		rt = SortableTable(parent, automultilineHeaders = False)
		self.resultsTable = rt
		columns = {}
		fval = "lambda e: float(e['%s'])"
		sval = "lambda e: ' '.join(e['%s'].split())"
		lval = "lambda e: ', '.join(e['%s'])"
		val= "lambda e: e.get('%s','')"
		def cite(e):
			return ('%s\n%s\n%s %s (%s) %s-%s' %
				(' '.join(e['title'].split()),
				 e.get('citationAuthorList',''),
				 e.get('citationJournalName',''),
				 e.get('citationJournalYear',''),
				 e.get('citationJournalVolume',''),
				 e.get('citationJournalFirstPage',''),
				 e.get('citationJournalLastPage','')))
		headings = (('ID', sval % 'accessionCode', 'nw', 0),
			    ('Sample Name', sval % 'sampleName', 'nw', '6c'),
			    ('Reference', cite, 'nw', '10c'),
			    ('Resolution', fval % 'resolution', 'n', 0),
			    ('Release Date', val % 'mapReleaseDate', 'n', 0),
			    ('Fit PDBs', val % 'fittedPDBidList', 'nw', '6c'),
			    )
                for h, vfunc, a, w in headings:
                        c = rt.addColumn(h, vfunc, format="%s", wrapLength = w,
					 anchor = a, entryPadX = 10, entryPadY = 5,
					 headerPadX = 10, headerPadY = 5, font = 'TkTextFont')
			columns[h] = c
                rt.sortBy(columns["ID"])
		rt.setData(self.results)
		rt.grid(row=row, column=0, sticky="nsew")
		rt.launch()
		parent.rowconfigure(row, weight=1)
		parent.columnconfigure(0, weight=1)
		
		row += 1

	def FetchMap(self):
		self.fetch()

	def FetchMapandPDBs(self):
		self.fetch(pdb = True)

	def fetch(self, pdb = False):
                slist = self.resultsTable.selected()
                import fetch_emdb_map as f
                for e in slist:
                        f.fetch_emdb_map(e['accessionCode'],
					 open_fit_pdbs = pdb)

	def destroy(self):
		chimera.extension.manager.deregisterInstance(self)
		ModelessDialog.destroy(self)

	def emHide(self):
		"""Extension manager method"""
		self.Close()
	Hide = emHide

	def emName(self):
		"""Extension manager method"""
		return self.title

	def emQuit(self):
		"""Extension manager method"""
		self.destroy()
	Quit = emQuit

	def emRaise(self):
		"""Extension manager method"""
		self.enter()
