from chimera.baseDialog import ModelessDialog, AskYesNoDialog

import chimera
from chimera import tkoptions
from chimera.HtmlText import HtmlText
from chimera.WizShell import WizShell

import Tkinter, Pmw

import BugReport
from BugReport import BUG_URL, post_url

import os

class BugReportGUI(WizShell):
    name            = "Bug Report Dialog"
    provideStatus   = True
    statusPosition  = 'left'
    oneshot         = True

    def __init__(self):
	pf = chimera.pathFinder()

	ROOT = pf.dataRoot

	img_src = os.path.join(ROOT, "BugReport", "1bug1.png")

	WizShell.__init__(self, 3, 200, 300, img_src, img_bg_color="white")


	self.createIntroPanel()

	if not self.checkConnection():
	    self.introText.configure(state='normal')
	    self.introText.delete(0.0, 'end')
	    self.introText.insert(0.0, "<font color=\"red\" size=\"+4\">"
		"Can't find network connection!</font>"
		"<p>Thank you for assisting us in the development process"
		" by using our feedback submission system."
		"  It does not appear that you are connected to the internet."
		"  A network connection is needed in order to send the"
		" feedback to the UCSF Computer Graphics Lab."
		"  Please try again when your computer is connected to a"
		" network.</p>"
		"<p>If you <i>do have</i> a network connection,"
		" but use a proxy to connect to the web,"
		" you can try configuring the proxy settings in the"
		" <a href=\"python:import dialogs, chimera;dialogs.display('preferences')."
		"setCategoryMenu(chimera.initprefs.WEBACCESS_PREF)\" "
		"title=\"Click to open 'Web Access' preferences\"> "
		"Web Access</a> preference category."
		"  More information on how to do this can be found in the"
		" <a href=\"python:chimera.help.display('UsersGuide/preferences.html#Web Access')\""
		" title=\"'Web Access' Preference category documentation\">"
		" Preferences documentation</a>.</p>"
		)
	    self.introText.configure(state='disabled')
	    self.buttonWidgets['Next'].configure(state='disabled')
	    self.buttonWidgets['Cancel'].configure(text='Try again later')

	self.createReportPanel()
	self.createResultPanel()

    def createIntroPanel(self):
	self.createTitle(0, "Submit a Bug")

	self.introText = HtmlText(self.pInterior(0), width=55, height=25,
						relief='flat', wrap='word')
	self.introText.pack(side='top', fill='both', expand=True, padx=10)

	self.introText.insert(0.0, "<p>Thank you for using our feedback system."
	    "  Feedback is greatly appreciated and plays a crucial role"
	    " in the development of Chimera.</p>"
	    "<p><b>Note</b>:  We do not automatically collect any personal"
	    " information or the data you were working with in Chimera when"
	    " the problem occurred."
	    "  Providing your e-mail address is optional,"
	    " but will allow us to contact you if more information is needed"
	    " and/or notify you when the bug has been fixed."
	    "  Any personal information you wish to provide should be"
	    " provided separately, and will kept strictly confidential.</p>"
	    )

	self.introText.configure(state='disabled',
			background=self.pInterior(0).cget('background'))

    def createReportPanel(self):
	self.createTitle(1, "Provide Information")

	self.createExplanation(1,
		"The information included in the Gathered Information area"
		" below may be insufficient to diagnose the problem."
		"  So please provide a description of how the problem"
		" occurred and an email address that can used to contact"
		" your for more information.", height=5, width=60)

	## consider using htmltext here instead of fields - no need for them,
	## since they can't be changed.....

	self.entry_widgets = {}

	self.entryFrame = Tkinter.Frame(self.pInterior(1))

	self.name_entry = tkoptions.StringOption(self.entryFrame,
		0, 'Contact Name', None, None, balloon="Your name")
	self.entry_widgets['name'] = self.name_entry

	self.email_entry = tkoptions.StringOption(self.entryFrame,
		1, 'E-mail Address', None, None,
		balloon="Who to notify when the bug is fixed or to ask for additional information")
	self.entry_widgets['email'] = self.email_entry

	desc_label = Tkinter.Label(self.entryFrame, text="Description:",
		justify='right')
	desc_label.grid(row=2, column=0, sticky=Tkinter.E, pady=10)

	self.description_text = Pmw.ScrolledText(self.entryFrame,
		text_pyclass=HtmlText,
		text_relief='sunken', text_height=6,
		text_width=50, text_wrap='word')
	self.description_text.grid(row=2, column=1, sticky='news', pady=10)
	self.entry_widgets['description'] = self.description_text
	self.entryFrame.rowconfigure(2, weight=1)
	from chimera import help
	help.register(self.description_text, balloon=BugReport.ADDL_INFO)

	info_label = Tkinter.Label(self.entryFrame,
			text="Gathered \nInformation:", justify='right')
	info_label.grid(row=3, column=0, sticky=Tkinter.E, pady=10)

	self.gathered_info = Pmw.ScrolledText(self.entryFrame,
		text_pyclass=HtmlText,
		text_relief='sunken', text_height=4,
		text_width=50, text_wrap='word')
	self.gathered_info.grid(row=3, column=1, sticky='news', pady=10)
	self.entry_widgets['info'] = self.gathered_info
	help.register(self.gathered_info,
                      balloon="Chimera-supplied information")

	self.file_chooser = tkoptions.InputFileOption(self.entryFrame,
		4, 'File Attachment', None, None,
		balloon='Choose a file to upload')
	self.entry_widgets['filename'] = self.file_chooser

	self.platform_entry = tkoptions.StringOption(self.entryFrame,
		5, 'Platform*', None, None,
		balloon="Your operating system and windowing system")
	self.entry_widgets['platform'] = self.platform_entry

	self.version_entry = tkoptions.StringOption(self.entryFrame,
		6, 'Chimera Version*', None, None,
		balloon="Specific version of chimera")
	self.entry_widgets['version'] = self.version_entry

	self.include_model_info = Tkinter.IntVar(self.entryFrame)
	self.include_model_info.set(True)
	Tkinter.Checkbutton(self.entryFrame, variable=self.include_model_info,
		text="Include open model names in bug report").grid(
		row=7, column=0, columnspan=2)

	self.entryFrame.columnconfigure(1, weight=1)

	self.entryFrame.pack(side='top', fill='both', expand=True)


    def createResultPanel(self):
	self.res_text = Pmw.ScrolledText(self.pInterior(2), text_width=55,
		text_height=35, text_wrap='word',
		text_relief='flat',
		text_pyclass=HtmlText)

	self.res_text.pack(fill='both', expand="True")
	self.res_text.configure(text_background=self.pInterior(2).cget('background'))



    def getHtmlRepr(self, br, label, field):
	FIELD_LABEL   = "<pre><b>%s:</b>\n     "
	NONE_GIVEN    = "<i>(None given)</i></pre>"
	FIELD_CONTENT = "%s</pre>"

	html_str = FIELD_LABEL % label

	if not getattr(br, field):
	    return html_str + NONE_GIVEN
	else:
	    content = getattr(br, field)
	    if len(content.split("\n")) == 1:
		return html_str + FIELD_CONTENT % content
	    else:
		return html_str + FIELD_CONTENT % content.replace("\n",
								"\n     ")


    def setBugReport(self, br):
	for k, w in self.entry_widgets.items():
	    val = br.getValue(k)
	    if val is None:
		continue
	    if hasattr(w, 'set'):
		w.set(val)
	    elif hasattr(w, 'settext'):
		w.settext(val)
	    elif hasattr(w, 'setentry'):
		    w.setentry(val)

	#self.entry_widgets['platform'].component('entry').configure(state='disabled')
	#self.entry_widgets['version'].component('entry').configure(state='disabled')
	#self.entry_widgets['info'].configure(text_state=Tkinter.DISABLED)
	self.entry_widgets['platform'].disable()
	self.entry_widgets['version'].disable()

    def reportOn(self, errcode, errmsg, headers, body):
	self.res_text.configure(text_state='normal')
	self.res_text.clear()
	self.res_text.insert(0.0, "<pre> %s\n\n%s\n\n%s\n\n%s </pre>" %
		(errcode, errmsg, headers, body)
		)

    def reportSuccess(self, br):
	self.status("Successfully submitted report...", color="blue",
								blankAfter=20)

	self.res_text.configure(text_state='normal')
	self.res_text.clear()

	text_content = ("<h3>Thank you for your report.</h3>"
		"<p>Your report will be evaluated by a Chimera developer"
		" and if you provided an e-mail address,"
		" then you will be contacted with a report status."
		"  More information about various Chimera mailing"
		" lists can be found on the"
		" <a href=\"http://www.cgl.ucsf.edu/chimera/docs/feedback.html\">"
		" Chimera feedback page</a>.</p>"
		"<p>The following information was submitted:")

	self.res_text.insert(0.0, text_content)

	self.res_text.insert('end',
			self.getHtmlRepr(br, "Contact Name", 'name'))
	self.res_text.insert('end',
			self.getHtmlRepr(br, "E-mail Address", 'email'))
	self.res_text.insert('end',
			self.getHtmlRepr(br, "Platform", 'platform'))
	self.res_text.insert('end',
			self.getHtmlRepr(br, "Chimera Version", 'version'))
	#self.res_text.insert('end',
	#		self.getHtmlRepr(br, "Python Traceback", 'traceback'))
	self.res_text.insert('end',
			self.getHtmlRepr(br, "Bug Description", 'description'))
	self.res_text.insert('end',
			self.getHtmlRepr(br, "File Attachment", 'filename'))

	self.res_text.configure(text_state='disabled')

    def reportFailure(self, br):
	self.status("Error submitting report...", color="red", blankAfter=20)

	self.res_text.configure(text_state='normal')
	self.res_text.clear()

	text_content = ("<h3>Error while submitting feedback.</h3>"
		"<p>An error occured when trying to submit your feedback."
		"  No information was received by the Computer Graphics Lab."
		"  This could be due to network problems, but more likely,"
		" there is a problem with Computer Graphics Lab's server."
		"  Please report this problem by sending email to"
		" <font color=\"blue\">chimera-bugs@cgl.ucsf.edu</font>.</p>"
		"<p>We apologize for any inconvenience, and do appreciate"
		" you taking the time to provide us with valuable feedback.")

	self.res_text.insert(0.0, text_content)

	self.res_text.configure(text_state='disabled')


    def checkResponse(self, errcode, errmsg):
	if int(errcode) == 200:
	    return True
	else:
	    return False

    def Next(self):

	WizShell.Next(self)

	if self.getCurrentPanel() == 1:
	    self.buttonWidgets['Next'].configure(text='Submit',
		    					command=self.Submit)

	if self.getCurrentPanel() == 2:
	    self.buttonWidgets['Cancel'].configure(text='Close')
	    self.buttonWidgets['Next'].configure(text='Next', state='disabled')
	    self.buttonWidgets['Back'].configure(state='disabled')

    def checkConnection(self):
	import urllib
	try:
	    file = urllib.urlopen(BUG_URL)
	except IOError:
	    return False
	return True

    def validateFields(self, bug_report):
	# platform and version are automatically filled in

	desc = bug_report.description
	email = bug_report.email

	if not email and ((not desc) or (BugReport.ADDL_INFO in desc)):
	    class MissingEmail(AskYesNoDialog):
		buttons = ("Back to Form", "Submit Anyway")
		default = buttons[0]
		def __init__(self):
		    AskYesNoDialog.__init__(self, 
			"Please include your email address so we can notify\n"
			"you when the bug is fixed or ask for additional\n"
			"information.  Otherwise, please describe what you\n"
			"where doing when the bug occurred.", justify='left')
		BacktoForm = AskYesNoDialog.Yes
		SubmitAnyway = AskYesNoDialog.No
	    if MissingEmail().run(self._toplevel) == 'yes':
		return False
	return True

    def Back(self):

	WizShell.Back(self)

	if self.getCurrentPanel() == 0:
	    self.buttonWidgets['Next'].configure(text='Next', command=self.Next)

	if self.getCurrentPanel() == 1:
	    self.buttonWidgets['Next'].configure(text='Submit',
		    					command=self.Submit)
	    self.buttonWidgets['Cancel'].configure(state='normal')


    def Submit(self):

	entry_values = {}

	# maps the name of the field 'name' to the value
	# that the user input: 'joe smith'
	for k, v in self.entry_widgets.items():
	    user_input = v.get().strip()
	    entry_values[k] = user_input


	bReport = BugReport.BugReport(includeSysInfo=False, **entry_values)

	if not self.validateFields(bReport):
	    return

	# include model names in description
	if self.include_model_info.get():
		entry_values['description'] += "\n\nOpen models\n"
		for m in chimera.openModels.list():
			entry_values['description'] += "%s %s\n" % (
				m.oslIdent(), getattr(m, 'name', "(no name)"))

	# fold info field into description
	info = entry_values['info']
	if info:
	    entry_values['description'] += "\n\n" + info
	del entry_values['info']

	from pyWidgetInterface import hidden_attrs, FILE_FIELD
	my_attrs = hidden_attrs.copy()

	for hk, hv in my_attrs.items():
	    for k, v in entry_values.items():
		if k.upper() + "_VAL" == hv:
		    my_attrs[hk] = v

	#from pprint import pprint
	#pprint(hidden_attrs)

	file_path = bReport.filename
	if file_path:
	    if not os.path.isfile(file_path):
		self.status("Couldn't locate file '%s'."
		    "  Please choose a valid file."
		    % os.path.split(file_path)[1], color='red')
		return
	    try:
		file_content = open(file_path, 'rb').read()
	    except IOError, what:
		error_msg = "Couldn't read file '%s' (%s)" % (
			os.path.split(file_path)[1],
			os.strerror(what.errno))
		self.status(error_msg, color='red')
		return

	    file_list = [(FILE_FIELD, os.path.split(file_path)[1], file_content)]
	else:
	    file_list = []

	self.status("Contacting CGL....", color="blue")

	errcode, errmsg, headers, body = post_url(my_attrs, file_list)

	if self.checkResponse(errcode, errmsg):
	    self.reportSuccess(bReport)
	else:
	    self.reportFailure(bReport)

	self.Next()


class BugNotification(ModelessDialog):

    buttons = ('Close', 'Report Bug')
    oneshot = True
    title   = "Problem encountered"

    def __init__(self, exp, content):
	self.exp = exp
	self.content = content

	ModelessDialog.__init__(self)


    def fillInUI(self, parent):

	header = "The following problem has been detected:\n\n"
	footer = ("\n\nBy clicking on the 'Report Bug' button below, you can\n"
		"notify the Chimera developers of this problem so that it\n"
		"can be fixed in future releases.")


	self.explanation = Tkinter.Label(parent, text=header + self.exp + footer)
	self.explanation.pack()

    def ReportBug(self):
	br_gui = BugReport.displayDialog()
	if not br_gui:
	    return

	bug_report = BugReport.BugReport(info=self.content)
	br_gui.setBugReport(bug_report)

	self.Close()
