# -----------------------------------------------------------------------------
# Fetch crystallographic density maps from the Upsalla Electron Density Server.
#
# ftp://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-1535/map/emd_1535.map.gz
# ftp://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-1535/header/emd-1535.xml
#

# -----------------------------------------------------------------------------
#
def fetch_emdb_map(id, open_fit_pdbs = False, open_models = True):

  site = 'ftp.ebi.ac.uk'
  url_pattern = 'ftp://%s/pub/databases/emdb/structures/EMD-%s/map/%s'
  xml_url_pattern = 'ftp://%s/pub/databases/emdb/structures/EMD-%s/header/%s'

  from chimera.replyobj import status, info
  status('Fetching %s from %s...\n' % (id,site), blankAfter = False)

  # Fetch map.
  map_name = 'emd_%s.map' % id
  map_gz_name = map_name + '.gz'
  map_url = url_pattern % (site, id, map_gz_name)
  name = 'EMDB %s' % id
  minimum_map_size = 8192       # bytes
  from chimera import fetch
  map_path, headers = fetch.fetch_file(map_url, name, minimum_map_size,
                                       'EMDB', map_name, uncompress = True)
    
  # Display map.
  status('Opening map %s...\n' % map_name, blankAfter = False)
  from VolumeViewer import open_volume_file
  models = open_volume_file(map_path, 'ccp4', map_name, 'surface',
                            open_models = open_models)

  if open_fit_pdbs:
    # Find fit pdb ids.
    status('EMDB %s: looking for fits PDBs\n' % id)
    pdb_ids = fit_pdb_ids_from_web_service(id)
    msg = ('EMDB %s has %d fit PDB models: %s\n'
           % (id, len(pdb_ids), ','.join(pdb_ids)))
    status(msg)
    info(msg)
    if pdb_ids:
      mlist = []
      from chimera import _openPDBIDModel, openModels
      for pdb_id in pdb_ids:
        status('Opening %s\n' % pdb_id)
        if open_models:
          m = openModels.open(pdb_id, 'PDBID')
        else:
          m = _openPDBIDModel(pdb_id)
        mlist.extend(m)
      models.extend(mlist)

  return models
  
# -----------------------------------------------------------------------------
#
def fit_pdb_ids_from_xml(xml_file):

  # ---------------------------------------------------------------------------
  # Handler for use with Simple API for XML (SAX2).
  #
  from xml.sax import ContentHandler
  class EMDB_SAX_Handler(ContentHandler):

    def __init__(self):
      self.pdbEntryId = False
      self.ids = []

    def startElement(self, name, attrs):
      if name == 'pdbEntryId':
        self.pdbEntryId = True

    def characters(self, s):
      if self.pdbEntryId:
        self.ids.append(s)

    def endElement(self, name):
      if name == 'pdbEntryId':
        self.pdbEntryId = False

    def pdb_ids(self):
      return (' '.join(self.ids)).split()

  from xml.sax import make_parser
  xml_parser = make_parser()

  from xml.sax.handler import feature_namespaces
  xml_parser.setFeature(feature_namespaces, 0)

  h = EMDB_SAX_Handler()
  xml_parser.setContentHandler(h)
  xml_parser.parse(xml_file)

  return h.pdb_ids()

# -----------------------------------------------------------------------------
#
def fit_pdb_ids_from_web_service(id):

  from WebServices.emdb_client import EMDB_WS
  ws = EMDB_WS()
  results = ws.findFittedPDBidsByAccessionCode(id)
  pdb_ids = [t['fittedPDBid'] for t in ws.rowValues(results)]
  return pdb_ids

# -----------------------------------------------------------------------------
# Register to fetch EMDB maps using the command line and file prefixes.
#
def register_emdb_file_prefix():

  import chimera
  fi = chimera.fileInfo
  fm = lambda id: fetch_emdb_map(id, open_models = False)
  fi.register('EMDBID', fm, None, ['emdbID'], category = fi.VOLUME)
  ffm = lambda id: fetch_emdb_map(id, open_fit_pdbs = True, open_models = False)
  fi.register('EMDBFITID', ffm, None, ['emdbfitID'], category = fi.VOLUME)

# -----------------------------------------------------------------------------
# Register to fetch EMDB using the Chimera Fetch by Id dialog.
#
def register_emdb_fetch():

  from chimera.fetch import registerIdType as reg
  from emdb_search import search_emdb
  reg('EMDB', 4, '1535', fetch_emdb_map,
      'www.ebi.ac.uk/pdbe/emdb',
      'http://www.ebi.ac.uk/msd-srv/emsearch/atlas/%s_summary.html',
      search_emdb)
  reg('EMDB & fit PDBs', 4, '1048',
      lambda id: fetch_emdb_map(id, open_fit_pdbs = True),
      'www.ebi.ac.uk/pdbe/emdb',
      'http://www.ebi.ac.uk/msd-srv/emsearch/atlas/%s_summary.html',
      search_emdb)
