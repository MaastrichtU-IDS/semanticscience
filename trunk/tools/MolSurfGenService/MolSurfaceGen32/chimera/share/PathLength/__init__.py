# -----------------------------------------------------------------------------
# Print sum of lengths of selected bonds to status line and reply log.
#
def print_path_length():

  from chimera import selection
  bonds = selection.currentBonds()

  msg = '%d bonds with total length %g\n' % (len(bonds), path_length(bonds))
  from chimera import replyobj
  replyobj.status(msg)          # Show on status line
  replyobj.message(msg)         # Record in reply log

# -----------------------------------------------------------------------------
#
def path_length(bonds):

  length = 0
  for b in bonds:
    length += b.length()
  return length


# -----------------------------------------------------------------------------
# Print sum of lengths of selected bonds for each model to status line and
# reply log.
#
def print_model_path_lengths():

  from chimera import selection
  bonds = selection.currentBonds()

  mbonds = {}
  for b in bonds:
    m = b.molecule
    if m in mbonds:
      mbonds[m].append(b)
    else:
      mbonds[m] = [b]

  for m, bonds in mbonds.items():
    msg = ('%s: %d bonds with total length %g\n'
           % (m.name, len(bonds), path_length(bonds)))
    from chimera import replyobj
    replyobj.status(msg)          # Show on status line
    replyobj.message(msg)         # Record in reply log
