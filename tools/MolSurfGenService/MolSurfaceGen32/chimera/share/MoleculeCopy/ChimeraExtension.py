# -----------------------------------------------------------------------------
# Register mcopy command.
#
def mcopy_cmd(cmdname, args):
    from MoleculeCopy import mcopy_command
    mcopy_command(cmdname, args)

from Midas.midas_text import addCommand
addCommand('mcopy', mcopy_cmd, help = True)
