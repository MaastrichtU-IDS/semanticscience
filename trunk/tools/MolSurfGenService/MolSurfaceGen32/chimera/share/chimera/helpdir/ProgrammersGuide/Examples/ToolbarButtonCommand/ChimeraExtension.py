# The initial code is the same as for the ToolbarButtonExtension example
import chimera.extension

class MainChainEMO(chimera.extension.EMO):
    def name(self):
        return 'Backbone'

    def description(self):
        return 'display only protein backbone'

    def categories(self):
        return ['Utilities']

    def icon(self):
        return self.path('mainchain.tiff')

    def activate(self):
        self.module().mainchain()

chimera.extension.manager.registerExtension(MainChainEMO(__file__))

# Here we define two functions, one to handle the "mainchain" command,
# and one to handle the "~mainchain" command.
def mainchainCmd(cmdName, args):
	# Import the module's workhorse function.
	# It is imported inside the function definition so that
	# it does not slow down Chimera startup with extra imports
	# in the main scope.
	from ToolbarButtonCommand import mainchain

	# Import and use the Midas.midas_text doExtensionFunc procedure
	# to process typed arguments and call the mainchain() function
	# appropriately.  For a simple function like mainchain(), which
	# takes no arguments, using doExtensionFunc is probably overkill.
	# One could instead use the approach applied in the revMainchainCmd
	# function below and simply test for the presence of any
	# arguments (raising MidasError if any are found) and directly calling
	# the mainchain() function otherwise.  As implemented here, using
	# doExtensionFunc, if the user does provide arguments then
	# doExtensionFunc will raise an error complaining that there
	# were unknown keyword arguments supplied.
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(mainchain, args)

# The function for "~mainchain"
def revMainchainCmd(cmdName, args):
	# We are going to implement ~mainchain as a synonym for "display",
	# so we import runCommand which simplifies doing that.
	from chimera import runCommand
	from Midas import MidasError
	if args:
		# Raising MidasError will cause the error message
		# to show up in the status line as red text
		raise MidasError("~mainchain takes no arguments")
	# runCommand takes any legal command-line command and executes it.
	runCommand("display")

# Now actually register the "mainchain" command with the command interpreter
# by using addCommand().  The first argument is the command name and the
# second is the callback function for doing the work.  The 'revFunc' keyword
# specifies the function to implement "~mainchain".  The 'help' keyword has
# been omitted, therefore no help will be provided.
from Midas.midas_text import addCommand
addCommand("mainchain", mainchainCmd, revFunc=revMainchainCmd)
		
