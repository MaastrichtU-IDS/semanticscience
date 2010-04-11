PREF_SCALING = "scaling"
PREF_OLD_SCALING = "styles"	# before x-sections were available
PREF_XSECTION = "xsections"
PREF_ATOMS = "atoms"

pref = None
ScalingPage = "scaling"
XSectionPage = "xsection"
AtomsPage = "atoms"

def initialize(setCurrent=1):
	global pref
	if pref is not None:
		return
	from chimera import preferences
	pref = preferences.addCategory("Ribbon Styles",
					preferences.HiddenCategory)

	try:
		# Cannot use "setdefault" here since we need to
		# check for old preference name and save to
		# new preference name
		p = pref[PREF_SCALING]
	except KeyError:
		try:
			p = pref[PREF_OLD_SCALING]
		except KeyError:
			p = {}
		pref[PREF_SCALING] = p
	import scaling
	scaling.initialize(p)

	p = pref.setdefault(PREF_XSECTION, {})
	import xsection
	xsection.initialize(p)

	p = pref.setdefault(PREF_ATOMS, {})
	import atoms
	atoms.initialize(p)

	import chimera
	import SimpleSession
	chimera.triggers.addHandler(SimpleSession.SAVE_SESSION, saveSession,
					None)

from chimera.baseDialog import ModelessDialog
class RibbonStyleEditor(ModelessDialog):

	name = "Ribbon Style Editor"
	help = "ContributedSoftware/ribbonstyle/ribbonstyle.html"
	provideStatus = True

	def fillInUI(self, parent):
		import Tkinter, Tix
		self.restrictVar = Tkinter.IntVar(parent)
		self.restrictVar.set(1)
		cb = Tkinter.Checkbutton(parent,
				text="Restrict OK/Apply to current selection,"
					" if any",
				variable=self.restrictVar)
		cb.pack(side=Tkinter.BOTTOM)
		nb = self.notebook = Tix.NoteBook(parent)
		nb.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
		from scaling import ScalingEditor
		nb.add(ScalingPage, label="Scaling")
		self.style = ScalingEditor(nb.page(ScalingPage), self)
		from xsection import XSectionEditor
		nb.add(XSectionPage, label="Cross Section")
		self.xsection = XSectionEditor(nb.page(XSectionPage), self)
		from atoms import AtomsEditor
		nb.add(AtomsPage, label="Residue Class")
		self.atoms = AtomsEditor(nb.page(AtomsPage), self)

	def Apply(self):
		page = self.notebook.raised()
		restrict = self.restrictVar.get()
		if page == ScalingPage:
			self.style.Apply(restrict)
		elif page == XSectionPage:
			self.xsection.Apply(restrict)
		elif page == AtomsPage:
			self.atoms.Apply(restrict)

def edit():
	from chimera import dialogs
	dialogs.display(RibbonStyleEditor.name)

def saveSession(trigger, data, f):
	import scaling, xsection, atoms
	import chimera
	from SimpleSession import sessionID, sesRepr, autoRestorable
	userScalings = scaling.sessionSaveUsed()
	userXSections = xsection.sessionSaveUsed()
	userResidueClasses = atoms.sessionSaveUsed()
	residueData = []
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		if not autoRestorable(m):
			continue
		for r in m.residues:
			ident = sessionID(r)
			sc = scaling.sessionSaveResidue(r)
			xs = xsection.sessionSaveResidue(r)
			rc = atoms.sessionSaveResidue(r)
			residueData.append((ident, sc, xs, rc))
	restoringCode = \
"""
def restoreSession_RibbonStyleEditor():
	import SimpleSession
	import RibbonStyleEditor
	userScalings = %s
	userXSections = %s
	userResidueClasses = %s
	residueData = %s
	flags = RibbonStyleEditor.NucleicDefault1
	SimpleSession.registerAfterModelsCB(RibbonStyleEditor.restoreState,
				(userScalings, userXSections,
				userResidueClasses, residueData, flags))
try:
	restoreSession_RibbonStyleEditor()
except:
	reportRestoreError("Error restoring RibbonStyleEditor state")
"""
	f.write(restoringCode % (sesRepr(userScalings), sesRepr(userXSections),
			sesRepr(userResidueClasses), sesRepr(residueData)))

def restoreState(args):
	if len(args) == 4:
		userScalings, userXSections, userResidueClasses, residueData = args
		flags = 0
	else:
		userScalings, userXSections, userResidueClasses, residueData, flags = args

	import scaling, xsection, atoms
	import chimera, SimpleSession
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		m.updateRibbonData()
	scData = scaling.sessionRestoreUsed(userScalings)
	xsData = xsection.sessionRestoreUsed(userXSections)
	rcData = atoms.sessionRestoreUsed(userResidueClasses)
	for rId, sc, xs, rc in residueData:
		r = SimpleSession.idLookup(rId)
		atoms.sessionRestoreResidue(r, rc, rcData, flags)
		scaling.sessionRestoreResidue(r, sc, scData)
		xsection.sessionRestoreResidue(r, xs, xsData)

initialize()
from chimera import dialogs
dialogs.register(RibbonStyleEditor.name, RibbonStyleEditor)
