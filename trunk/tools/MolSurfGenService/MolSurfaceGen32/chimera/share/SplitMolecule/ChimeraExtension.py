def split_molecules(cmdname, args):
    import SplitMolecule
    SplitMolecule.split_molecules(cmdname, args)
    
import Midas.midas_text
Midas.midas_text.addCommand('split', split_molecules, help = True, changesDisplay=False)
