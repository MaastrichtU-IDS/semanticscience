def symmetry_copies(cmdname, args):
    import SymmetryCopies
    SymmetryCopies.symmetry_copies_command(cmdname, args)

def undo_symmetry_copies(cmdname, args):
    import SymmetryCopies
    SymmetryCopies.undo_symmetry_copies_command(cmdname, args)
    
import Midas.midas_text
Midas.midas_text.addCommand('sym', symmetry_copies, undo_symmetry_copies,
                            help = True)

def icos_volume_sym():
    import SymmetryCopies
    SymmetryCopies.set_volume_icosahedral_symmetry()

from Accelerators import add_accelerator
add_accelerator('ic', 'Assigned icosahedral symmetry to active volume',
                icos_volume_sym)
