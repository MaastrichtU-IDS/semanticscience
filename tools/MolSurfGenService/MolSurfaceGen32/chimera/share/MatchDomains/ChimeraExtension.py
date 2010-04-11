# -----------------------------------------------------------------------------
#
def align_backbones():
  'Superimpose molecules by pairing selected atoms from identical residues'
  import MatchDomains
  MatchDomains.align_backbones_using_selected_atoms()

# -----------------------------------------------------------------------------
#
def illustrate_alignment():
  'Draw slabs to illustrate a the relative orientations of two domains'
  import MatchDomains
  MatchDomains.illustrate_backbone_alignment()
  
# -----------------------------------------------------------------------------
#
from Accelerators import add_accelerator
add_accelerator('ab', 'Align backbones using selected atoms', align_backbones)
add_accelerator('ai', 'Illustrate backbone alignment based on selected atoms',
                illustrate_alignment)
