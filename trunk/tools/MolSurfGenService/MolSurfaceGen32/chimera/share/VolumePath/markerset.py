# -----------------------------------------------------------------------------
# Set of Markers and Links between them.
#
class Marker_Set:

  def __init__(self, name):

    self.name = name
    self.molecule = None         # Molecule model used for markers
    self.curve_model = None             # VRML smooth interpolated curve
    self.next_marker_id = 1
    self.atom_to_marker = {}
    self.bond_to_link = {}
    self.file_path = None
    self.close_callbacks = []

  # ---------------------------------------------------------------------------
  #
  def show_model(self, show):

    m = self.marker_molecule()
    m.display = show

  # ---------------------------------------------------------------------------
  #
  def marker_molecule(self, model_id = None):

    if self.molecule == None:
      from chimera import Molecule, openModels
      m = Molecule()
      m.name = self.name
      if model_id == None:
        id = subid = openModels.Default
      else:
        id, subid = model_id
      self.set_marker_molecule(m)
      openModels.add([m], baseId = id, subid = subid, noprefs = True)

    return self.molecule

  # ---------------------------------------------------------------------------
  # Used by session restore.
  #
  def set_marker_molecule(self, mol):

    self.molecule = mol
    mol.marker_set = self
    from chimera import addModelClosedCallback
    addModelClosedCallback(mol, self.model_closed_cb)

  # ---------------------------------------------------------------------------
  #
  def marker_model(self, model_id = None):

    return self.marker_molecule(model_id)

  # ---------------------------------------------------------------------------
  #
  def transform(self):

    molecule = self.marker_molecule()
    return molecule.openState.xform

  # ---------------------------------------------------------------------------
  #
  def set_transform(self, xform):

    molecule = self.marker_molecule()
    molecule.openState.xform = xform
  
  # ---------------------------------------------------------------------------
  #
  def place_marker(self, xyz, rgba, radius, id = None):

    if id == None:
      id = self.next_marker_id
      self.next_marker_id = self.next_marker_id + 1
    else:
      self.next_marker_id = max(self.next_marker_id, id + 1)
      
    m = Marker(self, id, xyz, rgba, radius)

    return m
  
  # ---------------------------------------------------------------------------
  #
  def atom_marker(self, atom):

    return self.atom_to_marker.get(atom)

  # ---------------------------------------------------------------------------
  #
  def markers(self):

    self.remove_deleted_markers()
    return self.atom_to_marker.values()
        
  # ---------------------------------------------------------------------------
  #
  def remove_deleted_markers(self):

    a2m = self.atom_to_marker
    for a,m in a2m.items():
      if a.__destroyed__:
        del a2m[a]
        
  # ---------------------------------------------------------------------------
  #
  def show_markers(self, show):

    if self.molecule:
      for a in self.molecule.atoms:
        a.display = show

  # ---------------------------------------------------------------------------
  #
  def links(self):

    self.remove_deleted_links()
    return self.bond_to_link.values()
        
  # ---------------------------------------------------------------------------
  #
  def remove_deleted_links(self):

    b2l = self.bond_to_link
    for b,l in b2l.items():
      if b.__destroyed__:
        del b2l[b]
  
  # ---------------------------------------------------------------------------
  #
  def show_links(self, show):

    if self.molecule == None:
      return

    from chimera import Bond
    if show:
      mode = Bond.Smart         # Display only if atoms are shown.
    else:
      mode = Bond.Never
    for b in self.molecule.bonds:
      b.display = mode

  # ---------------------------------------------------------------------------
  #
  def selected_markers(self):

    from chimera.selection import currentAtoms
    atoms = currentAtoms()
    markers = []
    for a in atoms:
      if self.atom_to_marker.has_key(a):
        markers.append(self.atom_to_marker[a])
    return markers

  # ---------------------------------------------------------------------------
  #
  def selected_links(self):

    links = []
    from chimera.selection import currentBonds
    bonds = currentBonds()
    for b in bonds:
      if self.bond_to_link.has_key(b):
        links.append(self.bond_to_link[b])
    return links

  # ---------------------------------------------------------------------------
  #
  def show_curve(self, radius = 0, band_length = 0,
                 segment_subdivisions = 10, circle_subdivisions = 15):

    m = self.molecule
    if m is None:
      return

    import tube
    s, plist = tube.tube_through_atoms(m.atoms, radius, band_length,
                                       segment_subdivisions,
                                       circle_subdivisions)
    if s is None:
      return

    s.name = 'path tracer curve'
    self.curve_parameters = (radius, band_length, segment_subdivisions)
    self.curve_model = s
    from chimera import addModelClosedCallback
    addModelClosedCallback(s, self.curve_model_closed_cb)

    import SimpleSession
    SimpleSession.noAutoRestore(s)

  # ---------------------------------------------------------------------------
  #
  def unshow_curve(self):

    if self.curve_model:
      from chimera import openModels
      openModels.close([self.curve_model])
      self.curve_model = None
  
  # ---------------------------------------------------------------------------
  #
  def save_as_xml(self, out):

    ea = getattr(self, 'extra_attributes', {})
    out.write('<marker_set name="%s"%s>\n' %
	      (self.name, attribute_strings(ea)))

    markers = self.markers()
    markers.sort(lambda m1, m2: cmp(m1.id, m2.id))
    for m in markers:
      id_text = 'id="%d"' % m.id
      xyz_text = 'x="%.5g" y="%.5g" z="%.5g"' % m.xyz()

      rgb = tuple(m.rgba()[:3])
      if rgb == (1,1,1):
        rgb_text = ''
      else:
        rgb_text = 'r="%.5g" g="%.5g" b="%.5g"' % rgb

      radius_text = 'radius="%.5g"' % m.radius()

      if m.note():
        note_text = ' note="%s"' % xml_escape(m.note())
        note_rgb = tuple(m.note_rgba()[:3])
        if note_rgb == (1,1,1):
          note_rgb_text = ''
        else:
          note_rgb_text = ' nr="%.5g" ng="%.5g" nb="%.5g"' % note_rgb
      else:
        note_text = ''
        note_rgb_text = ''
      
      ea = getattr(m, 'extra_attributes', {})

      out.write('<marker %s %s %s %s%s%s%s/>\n' %
                (id_text, xyz_text, rgb_text, radius_text,
                 note_text, note_rgb_text, attribute_strings(ea)))

    links = self.links()
    for e in links:
      id_text = 'id1="%d" id2="%d"' % (e.marker1.id, e.marker2.id)
      rgb_text = 'r="%.5g" g="%.5g" b="%.5g"' % e.rgba()[:3]
      radius_text = 'radius="%.5g"' % e.radius()
      ea = getattr(e, 'extra_attributes', {})
      out.write('<link %s %s %s%s/>\n' % (id_text, rgb_text, radius_text,
					  attribute_strings(ea)))
      
    out.write('</marker_set>\n')
      
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    self.molecule = None
    # Don't clear molecule.marker_set since close callbacks need that.
    self.next_marker_id = 1
      
    self.atom_to_marker = {}
    self.bond_to_link = {}

    for cb in self.close_callbacks:
      cb(self)
      
  # ---------------------------------------------------------------------------
  #
  def add_close_callback(self, cb):
    self.close_callbacks.append(cb)
  def remove_close_callback(self, cb):
    if cb in self.close_callbacks:
      self.close_callbacks.remove(cb)
      
  # ---------------------------------------------------------------------------
  #
  def curve_model_closed_cb(self, model):

    self.curve_model = None
    
  # ---------------------------------------------------------------------------
  #
  def close(self):

    if self.molecule:
      from chimera import openModels
      openModels.close([self.molecule])
      
    if self.curve_model:
      from chimera import openModels
      openModels.close([self.curve_model])
      self.curve_model = None

# -----------------------------------------------------------------------------
# Marker is implemented as a Chimera Atom.
#
class Marker:

  def __init__(self, marker_set, id, xyz, rgba, radius, atom = None):

    self.marker_set = marker_set
    self.id = id
    self.note_text = ''

    if atom:
      a = atom
    else:
      molecule = marker_set.marker_molecule()
      from chimera import elements, Coord, Atom, MolResId
      rid = MolResId(id)
      r = molecule.newResidue('marker', rid)
      a = molecule.newAtom('', elements.H)
      r.addAtom(a)
      c = Coord()
      c.x, c.y, c.z = xyz
      a.setCoord(c)                               # a.coord = c does not work
      a.radius = radius
      a.drawMode = Atom.Sphere
      a.color = chimera_color(rgba)

    self.atom = a

    marker_set.atom_to_marker[a] = self
  
  # ---------------------------------------------------------------------------
  #
  def show(self, show):

    self.atom.display = show
  
  # ---------------------------------------------------------------------------
  #
  def xyz(self):

    c = self.atom.coord()
    return (c.x, c.y, c.z)
  
  # ---------------------------------------------------------------------------
  #
  def set_xyz(self, xyz):

    from chimera import Coord
    c = Coord()
    c.x, c.y, c.z = xyz
    self.atom.setCoord(c)
  
  # ---------------------------------------------------------------------------
  #
  def rgba(self, allow_none = False):

    if allow_none and self.atom.color is None:
      return None
    import Molecule
    rgba = Molecule.atom_rgba(self.atom)
    return rgba
  
  # ---------------------------------------------------------------------------
  #
  def set_rgba(self, rgba):

    self.atom.color = chimera_color(rgba)

  # ---------------------------------------------------------------------------
  #
  def radius(self):

    return self.atom.radius
  
  # ---------------------------------------------------------------------------
  #
  def set_radius(self, radius):

    self.atom.radius = radius

  # ---------------------------------------------------------------------------
  #
  def note(self):

    t = self.atom.label
    if not t:
      t = self.note_text
    return t
  
  # ---------------------------------------------------------------------------
  #
  def set_note(self, note):

    self.note_text = note
    self.atom.label = note

  # ---------------------------------------------------------------------------
  #
  def note_rgba(self):

    a = self.atom
    c = a.labelColor
    if c:
      rgba = c.rgba()
    else:
      from Molecule import atom_rgba
      rgba = atom_rgba(a)
    return rgba
  
  # ---------------------------------------------------------------------------
  #
  def set_note_rgba(self, rgba):

    self.atom.labelColor = chimera_color(rgba)
  
  # ---------------------------------------------------------------------------
  #
  def show_note(self, show):

    a = self.atom
    if show:
      if not a.label:
        a.label = self.note_text
    else:
      self.note_text = a.label
      a.label = ''
  
  # ---------------------------------------------------------------------------
  #
  def note_shown(self):

    if self.atom.label:
      return True
    return False

  # ---------------------------------------------------------------------------
  #
  def select(self, only = False):

    from chimera.selection import setCurrent, addCurrent
    if only:
      setCurrent(self.atom)
    else:
      addCurrent(self.atom)

  # ---------------------------------------------------------------------------
  #
  def deselect(self):

    from chimera.selection import removeCurrent
    removeCurrent(self.atom)

  # ---------------------------------------------------------------------------
  #
  def links(self):

    bonds = self.atom.bonds
    llist = map(lambda b, b2m = self.marker_set.bond_to_link: b2m[b], bonds)
    return llist
    
  # ---------------------------------------------------------------------------
  #
  def linked_markers(self):

    atoms = self.atom.neighbors
    mlist = map(lambda a, a2m = self.marker_set.atom_to_marker: a2m[a], atoms)
    return mlist
  
  # ---------------------------------------------------------------------------
  #
  def linked_to(self, marker):

    b = self.atom.findBond(marker.atom)
    if b:
      return self.marker_set.bond_to_link[b]
    return None
    
  # ---------------------------------------------------------------------------
  #
  def delete(self):

    a = self.atom
    r = a.residue
    m = a.molecule

    ms = self.marker_set
    for b in a.bonds:
      ms.bond_to_link[b].delete()

    m.deleteAtom(a)
    if len(r.atoms) == 0:
      m.deleteResidue(r)
    self.atom = None
    del ms.atom_to_marker[a]
    
  # ---------------------------------------------------------------------------
  #
  def model(self):

    return self.marker_set.marker_model()
  
# -----------------------------------------------------------------------------
# Link is implemented as a Chimera Bond.
#
class Link:

  def __init__(self, marker1, marker2, rgba, radius, bond = None):

    self.marker1 = marker1
    self.marker2 = marker2

    ms = marker1.marker_set
    if bond:
      b = bond
    else:
      molecule = ms.marker_molecule()
      b = molecule.newBond(marker1.atom, marker2.atom)
    self.bond = b
    ms.bond_to_link[b] = self

    self.set_rgba(rgba)
    self.set_radius(radius)
  
  # ---------------------------------------------------------------------------
  #
  def show(self, show):
      
    from chimera import Bond
    if show:
      mode = Bond.Smart         # Display only if atoms are shown.
    else:
      mode = Bond.Never
      
    self.bond.display = mode
  
  # ---------------------------------------------------------------------------
  #
  def rgba(self, allow_none = False):

    if allow_none and self.bond.color is None:
      return None
    import Molecule
    rgba = Molecule.bond_rgba(self.bond)
    return rgba
    
  # ---------------------------------------------------------------------------
  #
  def set_rgba(self, rgba):

    self.bond.color = chimera_color(rgba)
    self.bond.halfbond = 0
    
  # ---------------------------------------------------------------------------
  #
  def radius(self):

    b = self.bond
    if b.drawMode == b.Wire:
      radius = 0.0
    else:
      radius = b.radius
    return radius
      
  # ---------------------------------------------------------------------------
  # In stick representation, bond radius is shown as bond order times the
  # molecule stick size.  Use the bond order to control radius.
  #
  def set_radius(self, radius):

    b = self.bond
    m = self.molecule()
    if radius == 0:
      b.drawMode = b.Wire
      b.radius = 1
    else:
      b.drawMode = b.Stick
      b.radius = radius

  # ---------------------------------------------------------------------------
  #
  def molecule(self):

    ms = self.marker1.marker_set
    molecule = ms.marker_molecule()
    return molecule

  # ---------------------------------------------------------------------------
  #
  def select(self, only = False):

    from chimera.selection import setCurrent, addCurrent
    if only:
      setCurrent(self.bond)
    else:
      addCurrent(self.bond)
    
  # ---------------------------------------------------------------------------
  #
  def deselect(self):

    from chimera.selection import removeCurrent
    removeCurrent(self.bond)
    
  # ---------------------------------------------------------------------------
  #
  def delete(self):

    b = self.bond
    b.molecule.deleteBond(b)
    self.bond = None
    ms = self.marker1.marker_set
    del ms.bond_to_link[b]
    
  # ---------------------------------------------------------------------------
  #
  def model(self):

    return self.marker_set.marker_model()
          
# -----------------------------------------------------------------------------
#
def chimera_color(rgba):

  if rgba is None:
    c = None
  else:
    from chimera import MaterialColor
    c = MaterialColor(*rgba)
  return c
  
# -----------------------------------------------------------------------------
# Make string name1="value1" name2="value2" ... string for XML output.
#
def attribute_strings(dict):

  s = ''
  for name, value in dict.items():
    s = s + (' %s="%s"' % (name, xml_escape(value)))
  return s
  
# -----------------------------------------------------------------------------
# Replace & by &amp; " by &quot; and < by &lt; and > by &gt; in a string.
#
def xml_escape(s):

  s1 = s.replace('&', '&amp;')
  s2 = s1.replace('"', '&quot;')
  s3 = s2.replace('<', '&lt;')
  s4 = s3.replace('>', '&gt;')
  s5 = s4.replace("'", '&apos;')
  return s5

# -----------------------------------------------------------------------------
#
def save_marker_sets(mslist, out):

  if len(mslist) > 1:
    out.write('<marker_sets>\n')
    
  for ms in mslist:
    ms.save_as_xml(out)

  if len(mslist) > 1:
    out.write('</marker_sets>\n')
  
# -----------------------------------------------------------------------------
#
def load_marker_set_xml(input):

  # ---------------------------------------------------------------------------
  # Handler for use with Simple API for XML (SAX2).
  #
  from xml.sax import ContentHandler
  class Marker_Set_SAX_Handler(ContentHandler):

    def __init__(self):

      self.marker_set_tuples = []
      self.set_attributes = None
      self.marker_attributes = None
      self.link_attributes = None

    # -------------------------------------------------------------------------
    #
    def startElement(self, name, attrs):

      if name == 'marker_set':
        self.set_attributes = self.attribute_dictionary(attrs)
        self.marker_attributes = []
        self.link_attributes = []
      elif name == 'marker':
        self.marker_attributes.append(self.attribute_dictionary(attrs))
      elif name == 'link':
        self.link_attributes.append(self.attribute_dictionary(attrs))

    # -------------------------------------------------------------------------
    # Convert Attributes object to a dictionary.
    #
    def attribute_dictionary(self, attrs):

      d = {}
      for key, value in attrs.items():
	d[key] = value
      return d

    # -------------------------------------------------------------------------
    #
    def endElement(self, name):

      if name == 'marker_set':
        mst = (self.set_attributes,
	       self.marker_attributes,
	       self.link_attributes)
        self.marker_set_tuples.append(mst)
        self.set_attributes = None
        self.marker_attributes = None
        self.link_attributes = None


  from xml.sax import make_parser
  xml_parser = make_parser()

  from xml.sax.handler import feature_namespaces
  xml_parser.setFeature(feature_namespaces, 0)

  h = Marker_Set_SAX_Handler()
  xml_parser.setContentHandler(h)
  xml_parser.parse(input)

  return create_marker_sets(h.marker_set_tuples)

# -----------------------------------------------------------------------------
#
def create_marker_sets(marker_set_tuples):

  marker_sets = []
  for set_attributes, marker_attributes, link_attributes in marker_set_tuples:
    name = str(set_attributes.get('name', ''))
    ms = Marker_Set(name)
    ms.extra_attributes = leftover_keys(set_attributes, ('name',))
    id_to_marker = {}
    for mdict in marker_attributes:
      id = int(mdict.get('id', '0'))
      x = float(mdict.get('x', '0'))
      y = float(mdict.get('y', '0'))
      z = float(mdict.get('z', '0'))
      r = float(mdict.get('r', '1'))
      g = float(mdict.get('g', '1'))
      b = float(mdict.get('b', '1'))
      radius = float(mdict.get('radius', '1'))
      note = str(mdict.get('note', ''))
      nr = float(mdict.get('nr', '1'))
      ng = float(mdict.get('ng', '1'))
      nb = float(mdict.get('nb', '1'))
      m = ms.place_marker((x,y,z), (r,g,b,1), radius, id)
      m.set_note(note)
      m.set_note_rgba((nr,ng,nb,1))
      e = leftover_keys(mdict, ('id','x','y','z','r','g','b', 'radius','note',
				'nr','ng','nb'))
      m.extra_attributes = e
      id_to_marker[id] = m
    for ldict in link_attributes:
      id1 = int(ldict.get('id1', '0'))
      id2 = int(ldict.get('id2', '0'))
      r = float(ldict.get('r', '1'))
      g = float(ldict.get('g', '1'))
      b = float(ldict.get('b', '1'))
      radius = float(ldict.get('radius', '0'))
      l = Link(id_to_marker[id1], id_to_marker[id2], (r,g,b,1), radius)
      e = leftover_keys(ldict, ('id1','id2','r','g','b', 'radius'))
      l.extra_attributes = e
    marker_sets.append(ms)

  return marker_sets

# -----------------------------------------------------------------------------
#
def leftover_keys(dict, keys):

  leftover = {}
  leftover.update(dict)
  for k in keys:
    if leftover.has_key(k):
      del leftover[k]
  return leftover

# -----------------------------------------------------------------------------
#
def pick_marker(pointer_x, pointer_y, marker_sets):

  from chimera import viewer as v, Atom
  time = 0
  cursor_name = ''
  v.recordPosition(time, pointer_x, pointer_y, cursor_name),
  objects = v.pick(pointer_x, pointer_y)
  atoms = filter(lambda obj: isinstance(obj, Atom), objects)
  if len(atoms) != 1:
    return None

  a = atoms[0]
  for marker_set in marker_sets:
    if marker_set.atom_to_marker.has_key(a):
      return marker_set.atom_to_marker[a]

  return None

# -----------------------------------------------------------------------------
#
def pick_marker_3d(xyz, marker_sets):

  from Matrix import apply_inverse_matrix, distance
  close = []
  for marker_set in marker_sets:
    ms_xyz = apply_inverse_matrix(marker_set.transform(), xyz)
    for m in marker_set.markers():
      d = distance(m.xyz(), ms_xyz)
      if d <= m.radius():
	close.append((d,m))

  if close:
    close.sort()
    dist, closest_marker = close[0]
    return closest_marker

  return None

# -----------------------------------------------------------------------------
#
def select_markers(markers, only = True):

  atoms = [m.atom for m in markers]
  from chimera.selection import setCurrent, addCurrent
  if only:
    setCurrent(atoms)
  else:
    addCurrent(atoms)

# -----------------------------------------------------------------------------
# Does not transfer markers to new marker set if different marker sets would
# be linked.  Returns None in that case.  Otherwise returns the number of
# markers transfered.
#
def transfer_markers(mlist, marker_set):

  markers = filter(lambda m, ms=marker_set: m.marker_set != ms, mlist)
  
  mtable = {}
  for m in markers:
    mtable[m] = 1

  for m in markers:
    for m2 in m.linked_markers():
      if not mtable.has_key(m2) and m2.marker_set != marker_set:
        return None        # Markers in different sets would be linked.

  # Copy markers
  mmap = {}
  xform = marker_set.transform()
  from Matrix import xform_xyz
  for m in markers:
    xyz = xform_xyz(m.xyz(), m.marker_set.transform(), xform)
    mcopy = marker_set.place_marker(xyz, m.rgba(), m.radius())
    mmap[m] = mcopy

  # Copy links
  for m in markers:
    for link in m.links():
      if link.marker1 == m:
        Link(mmap[link.marker1], mmap[link.marker2],
             link.rgba(), link.radius())

  # Delete original markers and links
  for m in markers:
    m.delete()

  return len(markers)

# -----------------------------------------------------------------------------
#
def marker_sets():

    from chimera import openModels as om, Molecule
    msets = [m.marker_set for m in om.list(modelTypes = [Molecule])
             if hasattr(m, 'marker_set')]
    return msets
  
# -----------------------------------------------------------------------------
#
def selected_markers():

    mlist = []
    for ms in marker_sets():
        mlist.extend(ms.selected_markers())
    return mlist
  
# -----------------------------------------------------------------------------
#
def selected_links():

    llist = []
    for ms in marker_sets():
        llist.extend(ms.selected_links())
    return llist

# -----------------------------------------------------------------------------
#
def find_marker_set_by_name(name):
    
    for ms in marker_sets():
        if ms.name == name:
            return ms
    return None

# -----------------------------------------------------------------------------
#
def open_marker_set(path):
    
    file = open(path, 'r')
    import markerset
    marker_sets = markerset.load_marker_set_xml(file)
    file.close()
    
    if len(marker_sets) == 1:
        marker_sets[0].file_path = path

# -----------------------------------------------------------------------------
#
class Marker_Set_Callbacks:

    def __init__(self):

        self.open_callbacks = []
        self.open_handler = None
        self.close_callbacks = []
        self.close_handler = None

    # --------------------------------------------------------------------------
    #
    def add_marker_set_opened_callback(self, cb):

        if self.open_handler is None:
            from chimera import openModels as om
            self.open_handler = om.addAddHandler(self.open_models_cb, None)
        self.open_callbacks.append(cb)

    # -------------------------------------------------------------------------
    #
    def open_models_cb(self, trigger_name, args, models):

        from chimera import Molecule
        msets = [m.marker_set for m in models
                 if isinstance(m, Molecule) and hasattr(m, 'marker_set')]
        if msets:
            for cb in self.open_callbacks:
                cb(msets)

    # --------------------------------------------------------------------------
    #
    def add_marker_set_closed_callback(self, cb):

        if self.close_handler is None:
            from chimera import openModels as om
            self.close_handler = om.addRemoveHandler(self.close_models_cb, None)
        self.close_callbacks.append(cb)

    # -------------------------------------------------------------------------
    #
    def close_models_cb(self, trigger_name, args, models):

        from chimera import Molecule
        msets = [m.marker_set for m in models
                 if isinstance(m, Molecule) and hasattr(m, 'marker_set')]
        if msets:
            for cb in self.close_callbacks:
                cb(msets)
                    

# -----------------------------------------------------------------------------
#
msc = Marker_Set_Callbacks()
add_marker_set_opened_callback = msc.add_marker_set_opened_callback
add_marker_set_closed_callback = msc.add_marker_set_closed_callback
