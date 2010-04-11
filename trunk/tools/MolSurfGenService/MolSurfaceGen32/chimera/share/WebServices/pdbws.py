#!/usr/local/bin/python2.5

import soap_encoding
from PdbWebServiceService_client import PdbWebServiceServiceLocator
from PdbWebServiceService_types import ns0

locator = PdbWebServiceServiceLocator()
pdbws = locator.getpdbws()
print pdbws

pdbcode = "1yti"
pdbcode = "3fx2"

from PdbWebServiceService_client import getIdStatusRequest
req = getIdStatusRequest(in0=pdbcode)
resp = pdbws.getIdStatus(req)
print type(resp._getIdStatusReturn)
print resp._getIdStatusReturn

from PdbWebServiceService_client import getPrimaryCitationTitleRequest
req = getPrimaryCitationTitleRequest(in0=pdbcode)
resp = pdbws.getPrimaryCitationTitle(req)
print type(resp._getPrimaryCitationTitleReturn)
print resp._getPrimaryCitationTitleReturn

from PdbWebServiceService_client import getAnnotationsRequest
req = getAnnotationsRequest(in0=pdbcode)
resp = pdbws.getAnnotations(req)
print type(resp._getAnnotationsReturn)
print resp._getAnnotationsReturn
