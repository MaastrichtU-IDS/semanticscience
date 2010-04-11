# -----------------------------------------------------------------------------
# Command to show crystal contacts.
#
# Syntax: crystalcontacts <molecule-id> <distance>
#                         [copies true|false]
#                         [replace true|false]
#
def crystal_contacts(cmdname, args):

    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(show_contacts, args,
                    specInfo = [('moleculeSpec','molecules','models'),])

# -----------------------------------------------------------------------------
#
def show_contacts(molecules, distance, copies = False, replace = True):

    from chimera import Molecule
    mlist = [m for m in molecules if isinstance(m, Molecule)]

    if len(mlist) == 0:
        from Midas import MidasError
	raise MidasError, 'No molecules specified'

    from CrystalContacts import show_crystal_contacts
    for m in mlist:
        show_crystal_contacts(m, distance, make_copies = copies,
	                      replace = replace)
