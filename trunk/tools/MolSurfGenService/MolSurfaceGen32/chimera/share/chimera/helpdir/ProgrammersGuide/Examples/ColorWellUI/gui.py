#    Import the standard Python modules used by the example code.
import os
import Tkinter

#    Import the additional modules and classes needed.
#    The ColorOption class facilitates interoperation between Chimera
#    colors and color wells (which use rgba colors).
import chimera
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import ColorOption
import ColorWellUI

class ColorWellDialog(ModelessDialog):
    #    ColorWellDialog is a "nameless" dialog.  See the
    #    "Extension-Specific User Interface" example for a more detailed
    #    explanation of Chimera dialogs.
    #
    #    ..  "Extension-Specific User Interface"  Main_ExtensionUI.html

    #    Set the title bar of the dialog to display 'Set Backbone Color'.
    title = 'Set Backbone Color'

    def fillInUI(self, master):
	#    Create a ColorOption instance.  The ColorOption will contain
	#    a descriptive label and a color well.  The arguments to the
	#    ColorOption constructor are:
	#     - master widget
	#     - row number to use when 'grid'ing the ColorOption into the
	#       master widget.  The default column is 0.  The tkoptions
	#       module contains other options besides ColorOption (e.g.
	#       StringOption), which are generally intended to be put in
	#       vertical lists, and therefore a row number is specified in
	#       the constructor.  In this example we are only using one
	#       option however.
	#     - option label.  This will be positioned to the left of the
	#       color well and a ":" will be appended.
	#     - The default value for this option.
	#     - A callback function to call when the option is set by the
	#       user (e.g. a color dragged to the well, or the well color
	#       edited in the color editor)
	#     - An optional ballon-help message
	#
	coloropt = ColorOption(master, 0, 'Backbone Color', None, self._setBackboneColor, balloon='Protein backbone color')

	#    Call '_updateBackboneColor' to make the color displayed
	#    in the color well reflect the current color of protein
	#    backbone atoms. While not strictly necessary, keeping the
	#    color in the well consistent with the color in the molecules
	#    enhances the extension usability.
	self._updateBackboneColor(coloropt)

    #    Define '_updateBackboneColor', which is used to make the color
    #    of a well reflect the color of protein backbone atoms.
    def _updateBackboneColor(self, coloroption):
	#    Loop through all atoms in all molecules, looking for protein
	#    backbone atoms. When one is found, its color is compared
	#    against the last color seen, 'theColor'. The first time this
	#    comparison is made, 'theColor' does not exist yet and a
	#    NameError exception is raised; this exception is caught,
	#    and 'theColor' is assigned the color of the atom.  All
	#    subsequent times, the comparison between atom color and
	#    'theColor' should work as expected. If the two colors are
	#    different, the color well is set to show that multiple colors
	#    are present and execution returns to the caller.  If the two
	#    colors are the same, the next atom is examined. If only one
	#    color is found among all protein backbone atoms (or zero if
	#    no molecules are present), then execution continues.
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
	    for a in m.atoms:
		if ColorWellUI.MAINCHAIN.match(a.name):
		    try:
			if a.color != theColor:
			    coloroption.setMultiple()
			    return
		    except NameError:
			theColor = a.color

	#    Set the color of the well to match 'theColor'.  There are
	#    two possible cases:
	#      1 'theColor' is not set (because there are no molecules),
	#      2 'theColor' is 'None' or a color object.
	#    The 'set' function will not result in a callback to
	#    '_setBackboneColor'.
	try:
	    #    Handle case 2.  Set the color well to the proper color
	    coloroption.set(theColor)
	except NameError:
	    #    Handle case 1.  Set the color well to show that no color
	    #    is present
	    coloroption.set(None)

    #    Define '_setBackboneColor', which is invoked each time the
    #    color in the well changes.  When called by the ColorOption,
    #    '_setBackboneColor' receives a single argument 'coloropt',
    #    which is the ColorOption instance.
    def _setBackboneColor(self, coloroption):
	#    Call the 'mainchain' function in the main package, with
	#    the color object corresponding to the color well color
	#    as its argument (which will be None if 'No Color' is 
	#    the current selection in the well), to set the color of
	#    backbone atoms.
	ColorWellUI.mainchain(coloroption.get())

#    Define the module variable 'dialog', which keeps track of the
#    dialog window containing the color well. It is initialized to
#    'None', and is assigned a usable value when the dialog is created.
dialog = None

#    Define 'showColorWellUI', which is invoked when the Chimera
#    toolbar button is pressed.
def showColorWellUI():
    #    Declare that the name 'dialog' refers to the global variable
    #    defined above.
    global dialog
    #    Check whether the dialog has already been created. If so,
    #    the dialog window is displayed by calling it's 'enter()'
    #    function, and then the rest of the function is skipped by returning.
    if dialog is not None:
	dialog.enter()
        return

    #	Otherwise, create the dialog.
    dialog = ColorWellDialog()

#    Create the Chimera toolbar button that invokes the 'showColorWellUI'
dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'ColorWellUI.tiff')
chimera.tkgui.app.toolbar.add(icon, showColorWellUI, 'Set Main Chain Color', None)
