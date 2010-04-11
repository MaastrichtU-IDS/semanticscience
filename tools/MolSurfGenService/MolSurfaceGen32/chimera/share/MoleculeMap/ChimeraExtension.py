# -----------------------------------------------------------------------------
# Register molmap command.
#
def molmap_cmd(cmdname, args):
    from MoleculeMap.molmap import molmap_command
    molmap_command(cmdname, args)

from Midas.midas_text import addCommand
addCommand('molmap', molmap_cmd, help = True)
