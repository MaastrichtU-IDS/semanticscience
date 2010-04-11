class QueryResult(object):
    """
    A common class for representing query result in a variety of formats, namely:

    xml   : as an XML string using the XML result format of the query language
    python: as Python objects
    json  : as JSON
    """
    def __init__(self,pythonResult):
        self.rt = pythonResult

    def serialize(self,format='xml'):
        pass