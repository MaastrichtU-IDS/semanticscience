# -----------------------------------------------------------------------------
# Code for tile command.
#
#   Syntax: tile <modelSpec>
#               [columns <N>]
#               [spacingFactor <f>]
#               [independentRotation true|false]
#               [viewAll true|false]
#
def tile_command(cmdname, args):

  if len(args) == 0:
    args = '#'
  from Commands import doExtensionFunc
  if cmdname.startswith('un'):
    f = untile
  else:
    f = tile
  doExtensionFunc(f, args, specInfo = [('modelSpec','models','models'),])

# -----------------------------------------------------------------------------
#
def tile(models, columns = None, spacingFactor = 1.0,
         independentRotation = True, viewAll = True):

    from Commands import CommandError, check_number
    if len(models) == 0:
      raise CommandError, 'No models specified'
    check_number(columns, 'columns', type = int, allow_none = True,
                 positive = True)
    check_number(spacingFactor, 'spacingFactor')

    import base
    base.tile(models, spacingFactor, columns, viewAll)

    if independentRotation:
      from chimera import openModels
      openModels.cofrMethod = openModels.Independent
      
# -----------------------------------------------------------------------------
#
def untile(models, viewAll = True):

    from Commands import CommandError
    if len(models) == 0:
      raise CommandError, 'No models specified'

    m0 = models[0]
    for m in models[1:]:
      m.openState.xform = m0.openState.xform

    from chimera import openModels as om, viewer
    if om.cofrMethod == om.Independent:
      om.cofrMethod = om.FrontCenter

    if viewAll:
      viewer.viewAll(resetCofrMethod=False)
