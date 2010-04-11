# -----------------------------------------------------------------------------
# Fetch crystallographic density maps from the Upsalla Electron Density Server.
#
#   2fofc:    http://eds.bmc.uu.se/eds/sfd/1cbs/1cbs.omap
#    fofc:    http://eds.bmc.uu.se/eds/sfd/1cbs/1cbs_diff.omap
#    Info:    http://eds.bmc.uu.se/cgi-bin/eds/uusfs?pdbCode=1cbs
# Holdings:   http://eds.bmc.uu.se/eds/eds_holdings.txt
#
def open_eds_2fofc_map(id):
  return fetch_eds_map(id, type = '2fofc')

# -----------------------------------------------------------------------------
#
def open_eds_fofc_map(id):
  return fetch_eds_map(id, type = 'fofc')

# -----------------------------------------------------------------------------
#
def fetch_eds_map(id, type = '2fofc', open_models = True):

  site = 'eds.bmc.uu.se'
  url_pattern = 'http://%s/eds/dfs/%s/%s/%s'

  # Fetch map.
  from chimera.replyobj import status
  status('Fetching %s from web site %s...\n' % (id,site), blankAfter = False)
  if type == 'fofc':
    map_name = id + '_diff.omap'
  elif type == '2fofc':
    map_name = id + '.omap'
  map_url = url_pattern % (site, id[1:3], id, map_name)
  name = 'map %s' % id
  minimum_map_size = 8192       # bytes
  from chimera import fetch
  map_path, headers = fetch.fetch_file(map_url, name, minimum_map_size,
                                       'EDS', map_name)
    
  # Display map.
  status('Opening map %s...\n' % map_name, blankAfter = False)
  from VolumeViewer import open_volume_file
  models = open_volume_file(map_path, 'dsn6', map_name, 'mesh',
                            open_models = open_models)
  status('\n')

  return models

# -----------------------------------------------------------------------------
# Register to fetch crystallographic maps from the Electron Density Server
# using the command line and file prefixes.
#
def register_eds_id_file_prefix():

  import chimera
  fi = chimera.fileInfo
  o2fofc = lambda id: fetch_eds_map(id, '2fofc', False)
  fi.register('EDSID', o2fofc, None, ['edsID'], category = fi.VOLUME)
  ofofc = lambda id: fetch_eds_map(id, 'fofc', False)
  fi.register('EDSDIFFID', ofofc, None, ['edsdiffID'], category = fi.VOLUME)

# -----------------------------------------------------------------------------
# Register to fetch crystallographic maps from the Electron Density Server
# using the Chimera Fetch dialog.
#
def register_fetch_gui():

  from chimera import fetch
  fetch.registerIdType('EDS (2fo-fc)', 4, '1a0m', open_eds_2fofc_map,
                       'eds.bmc.uu.se/eds',
                       'http://eds.bmc.uu.se/cgi-bin/eds/uusfs?pdbCode=%s')
  fetch.registerIdType('EDS (fo-fc)', 4, '1a0m', open_eds_fofc_map,
                       'eds.bmc.uu.se/eds',
                       'http://eds.bmc.uu.se/cgi-bin/eds/uusfs?pdbCode=%s')
