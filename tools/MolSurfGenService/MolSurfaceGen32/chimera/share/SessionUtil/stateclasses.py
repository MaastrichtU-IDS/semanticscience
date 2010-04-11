# -----------------------------------------------------------------------------
# Classes to hold the state of some Chimera objects.  These are for use with
# SessionUtil/objecttree.py and the SimpleSession module for saving and
# restoring the state of extensions.
#

# -----------------------------------------------------------------------------
#
class Model_State:

  version = 4

  state_attributes = ('name', 'id', 'subid', 'osl_identifier',
		      'display', 'xform', 'active',
                      'use_clip_plane', 'use_clip_thickness', 'clip_thickness',
                      'clip_plane_origin', 'clip_plane_normal',
                      'version')
  
  # ---------------------------------------------------------------------------
  #
  def state_from_model(self, model):

    self.name = model.name
    self.id = model.id
    self.subid = model.subid
    self.osl_identifier = model.oslIdent()
    self.display = model.display
    self.xform = Xform_State()
    self.xform.state_from_xform(model.openState.xform)
    self.active = model.openState.active
    self.use_clip_plane = model.useClipPlane
    self.use_clip_thickness = model.useClipThickness
    self.clip_thickness = model.clipThickness
    p = model.clipPlane
    self.clip_plane_origin = p.origin.data()
    self.clip_plane_normal = p.normal.data()
      
  # ---------------------------------------------------------------------------
  #
  def restore_state(self, model):

    model.name = self.name
    model.display = self.display
    model.openState.xform = self.xform.create_object()
    model.openState.active = self.active

    #
    # Record how model id number has been remapped.
    #
    if self.version >= 2:
      from SimpleSession import modelMap
      modelMap.setdefault((self.id, self.subid), []).append(model)
    else:
      from SimpleSession import updateOSLmap
      updateOSLmap(self.osl_identifier, model.oslIdent())

    if self.version >= 3:
      p = model.clipPlane
      import chimera
      p.origin = chimera.Point(*self.clip_plane_origin)
      n = chimera.Vector(*self.clip_plane_normal)
      if n.length == 0:
        n = chimera.Vector(0,0,-1)
      p.normal = n
      model.clipPlane = p
      model.clipThickness = self.clip_thickness
      model.useClipPlane = self.use_clip_plane
      if self.version >= 4:
        model.useClipThickness = self.use_clip_thickness

# -----------------------------------------------------------------------------
#
class Xform_State:

  version = 1

  state_attributes = ('translation', 'rotation_axis', 'rotation_angle',
		      'version')
  
  # ---------------------------------------------------------------------------
  #
  def state_from_xform(self, xform):

    t = xform.getTranslation()
    self.translation = (t.x, t.y, t.z)
    axis, angle = xform.getRotation()
    self.rotation_axis = (axis.x, axis.y, axis.z)
    self.rotation_angle = angle
    
  # ---------------------------------------------------------------------------
  #
  def create_object(self):

    import chimera
    xf = chimera.Xform()
    trans = apply(chimera.Vector, self.translation)
    xf.translate(trans)
    axis = apply(chimera.Vector, self.rotation_axis)
    xf.rotate(axis, self.rotation_angle)
    return xf
