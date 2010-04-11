#    Import the standard modules used in this example.
import re

#    Import the Chimera modules used in this example.
import chimera
from chimera import selection

#    Define a function that will select protein backbone atoms in the
#    main Chimera graphics window
def selBackbone(op=None):
    #    Define a regular expression for matching the names of protein backbone
    #    atoms (we do not include the carbonyl oxygens because they tend to
    #    clutter up the graphics display without adding much information).
    MAINCHAIN = re.compile("^(N|CA|C)$", re.I)

    #    The 'list' method of chimera.openModels will return a list of 
    #    currently open models, and takes several optional keyword arguments
    #    to restrict this list to models matching certain criteria.
    #    When called with no arguments, this method will
    #    return a list of all visible models, essentially models that
    #    were created by the user. Internally managed ('hidden') models, 
    #    such as the distance monitor pseudobondgroup, do not show up in this
    #    list. A list of hidden models can be obtained by setting the 
    #    optional keyword argument 'hidden' to True. 
    #    The 'all' argument (True/False) can be used to return a list of all open models
    #    (including both hidden and visible). Other optional arguments include: 
    #   'id' and 'subid', which restrict the returned list to models with the given
    #    id and subid, respectively, while 'modelTypes' (a list of model types, 
    #    i.e. '[chimera.Molecule]') will restrict the returned list to models
    #    of a particular type.
    bbAtoms = []
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            if MAINCHAIN.match(a.name):
	        bbAtoms.append(a)

    #    Create a selection instance that we can use to hold the protein
    #    backbone atoms.  We could have added the atoms one by one to the
    #    selection while we were in the above loop, but it is more efficient
    #    to add items in bulk to selections if possible.
    backboneSel = selection.ItemizedSelection()
    backboneSel.add(bbAtoms)

    #    Add the connecting bonds to the selection.  The 'addImplied' method
    #    of Selection adds bonds if both bond endpoint atoms are in the
    #    selection, and adds atoms if any of the atom's bonds are in the
    #    selection.  We use that method here to add the connecting bonds.
    backboneSel.addImplied()

    #    Change the selection in the main Chimera window in the manner
    #    indicated by this function's 'op' keyword argument. If op is
    #    'None', then use whatever method is indicated by the 'Selection Mode'
    #    item in Chimera's Select menu.  Otherwise, op should
    #    be one of: 'selection.REPLACE', 'selection.INTERSECT',
    #    'selection.EXTEND' or 'selection.REMOVE'.  
    #      -  'REPLACE' causes the Chimera selection to be replaced with
    #         'backboneSel'.
    #      -   'INTERSECT' causes the Chimera selecion to be intersected
    #          with 'backboneSel'.
    #      -   'EXTEND' causes 'backboneSel' to be appended to the Chimera
    #          selection.
    #      -   'REMOVE' causes 'backboneSel' to be unselected in the
    #          Chimera window.
    if op is None:
    	chimera.tkgui.selectionOperation(backboneSel)
    else:
	selection.mergeCurrent(op, backboneSel)
