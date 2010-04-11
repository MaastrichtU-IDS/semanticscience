# -----------------------------------------------------------------------------
# Fetch biological unit PDB files from the Probable Quaternary Structure Server.
#
#   Home page:      http://pqs.ebi.ac.uk/
#   Index of files: ftp://ftp.ebi.ac.uk/pub/databases/msd/pqs/
#   Download page:  http://pqs.ebi.ac.uk/pqs-bin/macmol.pl?filename=1a34
#   PDB file:       ftp://ftp.ebi.ac.uk/pub/databases/msd/pqs/macmol/1a34.mmol
#   Multiple files: ftp://ftp.ebi.ac.uk/pub/databases/msd/pqs/macmol/104l_1.mmol
#                   ftp://ftp.ebi.ac.uk/pub/databases/msd/pqs/macmol/104l_2.mmol
#
def open_pqs(id):

  models = read_pqs(id)
  from chimera import openModels
  openModels.add(models)
  return models

# -----------------------------------------------------------------------------
#
def read_pqs(id):

  site = 'ftp.ebi.ac.uk'
  url_pattern = 'ftp://%s/pub/databases/msd/pqs/macmol/%s'

  from chimera.replyobj import status

  # Fetch file(s).
  models = fetch_pqs(site, url_pattern, id)
  if len(models) == 0:
    for suffix in range(1,100):
      mlist = fetch_pqs(site, url_pattern, id, '_%d' % suffix)
      if len(mlist) == 0:
        break
      models.extend(mlist)
    if len(models) == 0:
      from chimera import NonChimeraError
      status('\n')
      raise NonChimeraError('PQS file %s not available.' % id)
  status('\n')

  return models

# -----------------------------------------------------------------------------
#
def fetch_pqs(site, url_pattern, id, suffix = ''):

  from chimera.replyobj import status
  status('Fetching %s%s from web site %s...\n' % (id,suffix,site),
         blankAfter = False)
  minimum_file_size = 2048       # bytes
  name = id + suffix + '.mmol'
  file_url = url_pattern % (site, name)
  from chimera import fetch, NonChimeraError
  try:
    file_path, headers = fetch.fetch_file(file_url, name, minimum_file_size,
                                          'PQS', name)
  except NonChimeraError:
    return []

  # Display file(s).
  status('Opening PQS file %s...\n' % name, blankAfter = False)
  from chimera import _openPDBModel
  mlist = _openPDBModel(file_path, identifyAs = name)

  return mlist

# -----------------------------------------------------------------------------
# Register to fetch biological unit files the Probable Quaternary Structure
# server using the command line and file prefixes.
#
def register_pqs_id_file_prefix():

  import chimera
  fi = chimera.fileInfo
  fi.register('PQSID', read_pqs, None, ['pqsID'], category = fi.STRUCTURE)

# -----------------------------------------------------------------------------
# Register to fetch biological unit files the Probable Quaternary Structure
# server using the Chimera Fetch dialog.
#
def register_fetch_gui():

  from chimera import fetch
  fetch.registerIdType('PQS', 4, '2cwj', open_pqs, 'pqs.ebi.ac.uk',
                       'http://pqs.ebi.ac.uk/pqs-bin/pqs-hits?px=%s')
