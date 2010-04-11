# -----------------------------------------------------------------------------
# Command to make surface with z height given volume data plane.
#
#   Syntax: topography <volumeSpec>
#                       [height <h>]
#                       [interpolation cubic|none]
#                       [meshType isotropic|slash|backslash]
#                       [colorMap rainbow|none]
#                       [smoothingFactor <f>]
#                       [smoothingIterations <i>]
#
def topography_command(cmdname, args):

  from Midas.midas_text import doExtensionFunc
  doExtensionFunc(make_surface, args,
                  specInfo = [('volumeSpec','volumes','models')])

# -----------------------------------------------------------------------------
#
def make_surface(volumes, height = None, interpolation = 'none',
                 meshType = 'isotropic', colorMap = 'rainbow',
                 smoothingFactor = 0.3, smoothingIterations = 0,
                 replace = True):

  from Midas.midas_text import error

  if not height is None and not isinstance(height, (float,int)):
    error('Invalid non-numeric height "%s"' % str(height))
    return
  
  if not interpolation in ('cubic', 'none'):
    error('Invalid interpolation "%s" (cubic, none)' % str(interpolation))
    return
  
  if not meshType in ('isotropic', 'slash', 'backslash'):
    error('Invalid meshType "%s" (isotropic, slash, backslash)'
          % str(meshType))
    return
  
  if not colorMap in ('rainbow', 'none'):
    error('Invalid colorMap "%s" (rainbow, none)' % str(colorMap))
    return

  if not isinstance(smoothingIterations, int):
    error('Smoothing iterations must be integer, got "%s"'
          % str(smoothingIterations))
    return
  if not isinstance(smoothingFactor, (float,int)):
    error('Smoothing factor must be number, got "%s"'
          % str(smoothingFactor))
    return

  volumes = replace_solid_models_by_volume(volumes)
  
  from VolumeViewer import Volume
  for v in volumes:
    if not isinstance(v, Volume):
      error('Model %s is not a volume' % v.name)
      return

  for v in volumes:
    
    if len([s for s in v.matrix_size() if s == 1]) != 1:
      error('Volume %s is not a plane, size (%d,%d,%d)' %
            ((v.name,) + tuple(v.matrix_size())))
      return
    
  from toposurf import create_volume_plane_surface
  for v in volumes:
    create_volume_plane_surface(v, height, interpolation, meshType, colorMap,
                                smoothingFactor, smoothingIterations,
                                replace = replace)

# -----------------------------------------------------------------------------
#
def replace_solid_models_by_volume(volumes):

  vol = set()
  from _volume import Volume_Model
  for v in volumes:
    if isinstance(v, Volume_Model):
      vol.add(solid_volume(v))
    else:
      vol.add(v)
  return list(vol)
    
# -----------------------------------------------------------------------------
#
def solid_volume(vm):

  from VolumeViewer import volume_list
  for v in volume_list():
    if vm in v.models():
      return v
  return None
