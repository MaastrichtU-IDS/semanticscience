# -----------------------------------------------------------------------------
# Create a surface model from a GRASP surface file.
#
def read_grasp_surface(path):

  sg = GRASP_Surface_Geometry(path)
  from _surface import SurfaceModel
  sm = SurfaceModel()
  import os.path
  sm.name = os.path.basename(path)
  rgba = (1, 1, 1, 1)
  p = sm.addPiece(sg.vertices, sg.triangles, rgba)
  p.normals = sg.normals
  return sm

# -----------------------------------------------------------------------------
#
class GRASP_Surface_Geometry:

  def __init__(self, path):

    self.path = path
    swap = self.need_to_swap_bytes(path)

    file = open(path, 'rb')

    file.seek(0,2)                              # goto end of file
    self.file_size = file.tell()
    file.seek(0,0)                              # goto beginning of file

    self.vertices, self.normals, self.triangles = \
      self.parse_records(file, swap)
    
    file.close()

  # ---------------------------------------------------------------------------
  #
  def parse_records(self, file, swap):
    
    fmt = self.read_record(file, swap)  # Text line "format=1" or "format=2"
    fmt = fmt.strip()
    if fmt == "format=1":
      format = 1
    elif fmt == "format=2":
      format = 2
    else:
      raise SyntaxError, 'First record must be "format=1" or "format=2", got "%s"' % fmt

    line2 = self.read_record(file, swap)
    field_names = line2.strip().split(',')
    self.skip_record (file, swap)               # Additional field names
    line4 = self.read_record(file, swap)
    vtot, itot, igrid, scale = self.parse_line_4(line4)
    self.skip_record(file, swap)                # midx, midy, midz values

    # Read arrays
    from numpy import float32, reshape, int16, int32, intc, subtract
    for field in field_names:
      if field == "vertices":
        vs = self.read_record(file, swap)
        v = string_values(vs, float32, swap)
        v = reshape(v, (vtot, 3))
      elif field == "normals":
        ns = self.read_record(file, swap)
        n = string_values(ns, float32, swap)
        n = reshape(n, (vtot, 3))
      elif field == "triangles":
        ts = self.read_record(file, swap)
        # Convert index base from 1 to 0.
        if format == 1:
          type = int16
        else:
          type = int32
        t = string_values(ts, type, swap)
        subtract(t, 1, t)
        t = t.astype(intc)
        t = reshape(t, (itot, 3))
      else:
        self.skip_record(file, swap)

    return v, n, t
  
  # ---------------------------------------------------------------------------
  # Line 4 is sometimes fortan-column-formatted (3i6, f12.6) and sometimes
  # white space separated.
  #
  def parse_line_4(self, line4):

    fields = line4.split()
    if len(fields) == 4:
      vtot = int(fields[0])
      itot = int(fields[1])
      igrid = int(fields[2])
      scale = float(fields[3])
    else:
      vtot = int(line4[0:6])
      itot = int(line4[6:12])
      igrid = int(line4[12:18])
      scale = float(line4[18:36])

    return vtot, itot, igrid, scale
    
  # ---------------------------------------------------------------------------
  #
  def need_to_swap_bytes(self, path):

    file = open(path, 'rb')
    from numpy import fromstring, int32
    v = fromstring(file.read(4), int32)[0]
    file.close()
    return (v < 0 or v >= 65536)
    
  # ---------------------------------------------------------------------------
  #
  def read_record(self, file, swap):

    from numpy import int32
    size = string_values(file.read(4), int32, swap)[0]
    if size < 0:
      raise SyntaxError, 'Negative record size %d' % size
    if size > self.file_size:
      raise SyntaxError, ('Record size %d > file size %d'
                          % (size, self.file_size))

    string = file.read(size)

    esize = string_values(file.read(4), int32, swap)[0]
    if esize != size:
      raise SyntaxError, ('Record size at end of record %d' % esize + 
                          ' != size at head of record %d' % size)
      
    return string
    
  # ---------------------------------------------------------------------------
  #
  def skip_record(self, file, swap):

    from numpy import int32
    size = string_values(file.read(4), int32, swap)[0]
    file.seek(size, 1)
    esize = string_values(file.read(4), int32, swap)[0]

# -----------------------------------------------------------------------------
#
def string_values(string, type, swap):

  from numpy import fromstring
  values = fromstring(string, type)
  if swap:
    values = values.byteswap()
  return values
