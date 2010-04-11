# -----------------------------------------------------------------------------
# Routines to extract PDB transformation matrices from PDB file header.
#

# -----------------------------------------------------------------------------
#
def pdb_smtry_matrices(pdb_headers):

  return pdb_remark_matrices(pdb_headers, '290', 'SMTRY')

# -----------------------------------------------------------------------------
#
def pdb_biomt_matrices(pdb_headers):

  return pdb_remark_matrices(pdb_headers, '350', 'BIOMT')
        
# -----------------------------------------------------------------------------
#
def pdb_remark_matrices(pdb_headers, remark_number, tag_name):

  h = pdb_headers
  if not h.has_key('REMARK'):
    return []

  remarks = h['REMARK']
  mtable = {}
  for r in remarks:
    fields = r.split()
    if (len(fields) < 8 or fields[0] != 'REMARK' or
	fields[1] != remark_number or fields[2][:-1] != tag_name):
      continue
    try:
      matrix_num = int(fields[3])
    except ValueError:
      continue
    if not mtable.has_key(matrix_num):
      mtable[matrix_num] = [None, None, None]
    try:
      row = int(fields[2][5]) - 1
    except ValueError:
      continue
    if row >= 0 and row <= 2:
      try:
        mtable[matrix_num][row] = tuple(map(float, fields[4:8]))
      except ValueError:
        continue

  # Order matrices by matrix number.
  msorted = map(lambda nm: nm[1], sorted(mtable.items()))
  matrices = filter(lambda mrows: mrows.count(None) == 0, msorted)
  matrices = map(tuple, matrices)

  return matrices

# -----------------------------------------------------------------------------
# The "given" flag indicates which MTRIX records should be returned.
# The PDB MTRIX records have a "given" field which indicates whether or
# not the transformed coordinates are already given in the PDB entry.
#
def pdb_mtrix_matrices(pdb_headers, add_identity = True, given = False):

  h = pdb_headers
  have_matrix = (h.has_key('MTRIX1') and
		 h.has_key('MTRIX2') and
		 h.has_key('MTRIX3'))
  if not have_matrix:
    if add_identity:
      import matrices
      return [matrices.identity_matrix()]
    else:
      return []

  row1_list = h['MTRIX1']
  row2_list = h['MTRIX2']
  row3_list = h['MTRIX3']
  if len(row1_list) != len(row2_list) or len(row2_list) != len(row3_list):
    if add_identity:
      import matrices
      return [matrices.identity_matrix()]
    else:
      return []
  
  row_triples = map(lambda m1, m2, m3: (m1, m2, m3),
		    row1_list, row2_list, row3_list)
  
  mlist = []
  for row_triple in row_triples:
    matrix = []
    for line in row_triple:
      try:
        mrow = map(float, (line[10:20], line[20:30], line[30:40], line[45:55]))
      except ValueError:
        break
      mgiven = (len(line) >= 60 and line[59] == '1')
      if (mgiven and given) or (not mgiven and not given):
        matrix.append(mrow)
    if len(matrix) == 3:
      mlist.append(tuple(matrix))

  if add_identity:
    import matrices
    if not filter(matrices.is_identity_matrix, mlist):
      # Often there is no MTRIX identity entry
      mlist.append(matrices.identity_matrix())

  return mlist
