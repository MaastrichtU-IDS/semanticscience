#!/usr/local/bin/python2.5

class EMDB_WS:

	ResultAttrList = [
            "accessionCode",
            "sampleName",
            "mapReleaseDate",
            "resolution",
            "fittedPDBidList",
            "title",
            "citationAuthorList",
            "citationJournalName",
            "citationJournalVolume",
            "citationJournalFirstPage",
            "citationJournalLastPage",
            "citationJournalYear",
            "contour",
            "fittedPDBid",
	]

	def __init__(self):
		from EMBusinessServiceService_client \
				import EMBusinessServiceServiceLocator
		from EMDB_response_xsd_types import ns0
		self.locator = EMBusinessServiceServiceLocator()
		self.emdbws = self.locator.getEMBusinessService()
		self.resultType = ns0.resultset_Dec()

	def _getResults(self, xml):
		from ZSI import ParsedSoap
		ps = ParsedSoap(xml, envelope=False)
		return ps.Parse(self.resultType)

	def rowValues(self, results):
		rv = []
		for row in results._row:
			values = {}
			for attr in self.ResultAttrList:
				try:
					v = getattr(row, "_" + attr)
					if v is not None:
						values[attr] = v
				except AttributeError:
					pass
			rv.append(values)
		return rv

	def dumpResults(self, results):
		for row in results._row:
			self._dumpRow(row)

	def _dumpRow(self, row):
		print row
		for attr in self.ResultAttrList:
			try:
				value = getattr(row, "_" + attr)
				if value is not None:
					print "  %s: %s" % (attr, value)
			except AttributeError:
				pass

	def getResultSetXMLByAuthor(self, author):
		from EMBusinessServiceService_client \
				import getResultSetXMLByAuthorRequest
		req = getResultSetXMLByAuthorRequest()
		req._authorname = author
		resp = self.emdbws.getResultSetXMLByAuthor(req)
		return self._getResults(resp._getResultSetXMLByAuthorReturn)

	def getResultSetXMLByID(self, accession):
		from EMBusinessServiceService_client \
				import getResultSetXMLByIDRequest
		req = getResultSetXMLByIDRequest()
		req._accession_code = accession
		resp = self.emdbws.getResultSetXMLByID(req)
		return self._getResults(resp._getResultSetXMLByIDReturn)

	def getResultSetXMLByTitle(self, title):
		from EMBusinessServiceService_client \
				import getResultSetXMLByTitleRequest
		req = getResultSetXMLByTitleRequest()
		req._title = title
		resp = self.emdbws.getResultSetXMLByTitle(req)
		return self._getResults(resp._getResultSetXMLByTitleReturn)

	def getSampleNameXML(self, id):
		from EMBusinessServiceService_client \
				import getSampleNameXMLRequest
		req = getSampleNameXMLquest()
		req._id = id
		resp = self.emdbws.getSampleNameXML(req)
		return self._getResults(resp._getSampleNameXMLReturn)

	def findContourLevelByAccessionCode(self, accession):
		from EMBusinessServiceService_client \
				import findContourLevelByAccessionCodeRequest
		req = findContourLevelByAccessionCodeRequest()
		req._accession_code = accession
		resp = self.emdbws.findContourLevelByAccessionCode(req)
		return self._getResults(
				resp._findContourLevelByAccessionCodeReturn)

	def findFittedPDBidsByAccessionCode(self, accession):
		from EMBusinessServiceService_client \
				import findFittedPDBidsByAccessionCodeRequest
		req = findFittedPDBidsByAccessionCodeRequest()
		req._accession_code = accession
		resp = self.emdbws.findFittedPDBidsByAccessionCode(req)
		return self._getResults(
				resp._findFittedPDBidsByAccessionCodeReturn)

	def searchSampleNameByID(self, id):
		from EMBusinessServiceService_client \
				import searchSampleNameByIDRequest
		req = searchSampleNameByIDRequest()
		req._id = id
		resp = self.emdbws.searchSampleNameByID(req)
		return self._getResults(
				resp._searchSampleNameByIDReturn)

if __name__ == "__main__":
	ws = EMDB_WS()
	accession = "1249"
	author = "taylor"
	title = "hiv"
	print "findContourLevelByAccessionCode", accession
	ws.dumpResults(ws.findContourLevelByAccessionCode(accession))
	print
	print "findFittedPDBidsByAccessionCode", accession
	ws.dumpResults(ws.findFittedPDBidsByAccessionCode(accession))
	print
	print "getResultSetXMLByID", accession
	ws.dumpResults(ws.getResultSetXMLByID(accession))
	print
	print "getResultSetXMLByAuthor", accession
	ws.dumpResults(ws.getResultSetXMLByAuthor(author))
	print
	print "getResultSetXMLByTitle", accession
	ws.dumpResults(ws.getResultSetXMLByTitle(title))
