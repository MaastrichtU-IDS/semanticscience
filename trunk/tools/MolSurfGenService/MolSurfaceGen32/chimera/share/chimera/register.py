import Tkinter as Tk, Pmw, urllib
from baseDialog import ModelessDialog
from chimera import replyobj

regURL      = "http://www.cgl.ucsf.edu/cgi-bin/chimera_registration.py"
usersURL = "http://www.cgl.ucsf.edu/mailman/subscribe/chimera-users" 
announceURL = "http://www.cgl.ucsf.edu/mailman/subscribe/chimera-announce" 

SubscribeFailure = (
    "An error occurred while attempting to "
    "subscribe to the Chimera %s mailing list.  "
    "Try subscribing manually by visiting the "
    "<a href=\"http://www.cgl.ucsf.edu/chimera/docs/feedback.html\">"
    "Chimera feedback page</a>.")
SubscribeOkay = (
    "You have been subscribed to the Chimera %s mailing list; "
    "look for a confirmation message in the e-mail "
    "account '%s'")

class RegDialog(ModelessDialog):
    name = "Registration"
    buttons = ('Register', 'Close')
    provideStatus = True
    usage_types = [
	'Research', 'Teaching', 'Presentation Graphics', 'Personal'
    ]
    org_types = [
	'Educational', 'Non-profit', 'Personal', 'Commercial'
    ]

    def fillInUI(self, parent):
        self.addInfo(parent)
        self.entries = self.addFields(parent)
        self.status("Click 'Register' to continue...\n")

    def map(self, e=None):
	# First check if the server can be accessed
	if self.checkConnection():
	    return
	else:
	    replyobj.pushMode(replyobj.ERROR)
	    replyobj.message(
			'There has been an error while trying to\n'
			'contact the server. Your registration cannot \n'
			'be processed at this time.\n\n'
	    		'If you use a proxy server to connect to the web,\n'
			'try configuring the proxy settings in the \n'
	    		'Web Access Preferences category, restarting \n'
	    		'Chimera, and trying again.\n')
	    replyobj.popMode()
	    self.Close()

    def checkIfRegistered(self):
        import registration
        return registration.checkRegistration(nag=0)
            
    def checkConnection(self):
	try:
	    file = urllib.urlopen(regURL)
	except IOError:
	    return False
	return True

    def addInfo(self, parent):
	self.infoFrame = Tk.Frame(parent)
	self.regGroup = Pmw.Group(self.infoFrame,
		tag_text="Chimera Registration")

        from chimera.HtmlText import HtmlText
	registered = self.checkIfRegistered()
	if registered:
	    height = 8
	else:
	    height = 6
        self.info = HtmlText(self.regGroup.interior(), height=height,
			relief='flat', wrap='word', highlightthickness=0)
	if registered:
	    self.info.insert(0.0,
		"<b>Your copy of Chimera is already registered</b><p>")
        self.info.insert(0.0,
		"Thank you for registering your copy of Chimera. "
		"Development of Chimera is supported in part through "
		"funding from the National Institutes of Health "
		"(grant P41-RR01081). By providing the information requested "
		"below you will be helping us document the impact this "
		"software is having in the scientific community. The "
		"information you supply will only be used "
		"for reporting summary usage statistics to NIH "
		"(i.e., no individual data will be reported to NIH).")
	self.info.configure(padx=5, pady=5, state="disabled")
	self.info.pack(side=Tk.TOP, fill=Tk.Y, anchor=Tk.W)
	self.regGroup.pack(side=Tk.TOP, fill=Tk.BOTH, padx=7, pady=4)
	self.infoFrame.pack(side=Tk.TOP, fill=Tk.BOTH)

    def addFields(self, parent):
	fields = ['*Name:\n(Last, First)', '*E-mail:', 'Organization:']
	entries = []

	self.entryFrame = Tk.Frame(parent, padx=5)

	self.entryLabel = Tk.Label(self.entryFrame,
		text="Please provide the following information, "\
		    "and click 'Register' ('*' denotes a required field). "\
		    "Chimera will install the registration key in the proper "\
		    "location.")
	self.entryLabel.config(wraplength=500, justify=Tk.LEFT)
	self.entryLabel.pack(side=Tk.TOP, fill=Tk.Y, anchor=Tk.W, pady=10)

	##Entry Fields
	for field in fields:
	    row = Tk.Frame(self.entryFrame)
	    lab = Tk.Label(row, width=15, text=field, justify=Tk.RIGHT)
	    ent = Tk.Entry(row)
	    row.pack(side=Tk.TOP, fill=Tk.X, pady=2)
	    lab.pack(side=Tk.LEFT, pady=2)
	    ent.pack(side=Tk.RIGHT, expand=Tk.YES, fill=Tk.X, pady=2)
	    entries.append(ent)

	##Radio Buttons for organization type
	self.orgTypeFrame = Tk.Frame(self.entryFrame)
	self.orgVar = Tk.StringVar(parent)

	lab = Tk.Label(self.orgTypeFrame, width=15, text='')
	lab.pack(side=Tk.LEFT)
	for type in self.org_types:
	    button = Tk.Radiobutton(self.orgTypeFrame, text=type,
				variable=self.orgVar, value=type)
	    button.pack(side=Tk.LEFT)

	self.orgTypeFrame.pack(side=Tk.TOP, fill=Tk.X)
	entries.append(self.orgVar)

	##Radio Buttons for software usage:
	self.usageFrame = Tk.Frame(self.entryFrame)
	self.usageVar = Tk.StringVar(parent)

	lab = Tk.Label(self.usageFrame, width=15,
		text='Will primarily\nbe used for:')
	lab.pack(side=Tk.LEFT)
	for use in self.usage_types:
	    button = Tk.Radiobutton(self.usageFrame, text=use,
				variable=self.usageVar, value=use)
	    button.pack(side=Tk.LEFT)

	self.usageFrame.pack(side=Tk.TOP, fill=Tk.X, pady=4)
	entries.append(self.usageVar)

	##for NIH 'fundedness'
	self.NIHFrame = Tk.Frame(self.entryFrame)
	self.nihVar = Tk.IntVar(parent)

	lab = Tk.Label(self.NIHFrame, width=2, text='')
	lab.pack(side=Tk.LEFT)
	self.nihChk = Tk.Checkbutton(self.NIHFrame,
	    text='This software will be used in support of NIH-funded research',
	    variable=self.nihVar)
	self.nihChk.pack(side=Tk.LEFT)

	self.NIHFrame.pack(side=Tk.TOP, fill=Tk.X)
	entries.append(self.nihVar)

        ## for chimera-users mailing list
        usersFrame = Tk.Frame(self.entryFrame)
        self.usersVar = Tk.IntVar(parent)
        self.announceVar = Tk.IntVar(parent)

	lab = Tk.Label(usersFrame, width=2, text='')
	lab.pack(side=Tk.LEFT)
	self.usersChk = Tk.Checkbutton(usersFrame,
                                          text="Add me to the Chimera users mailing list (chimera-users@cgl.ucsf.edu),\n" \
                                          "which is used for discussion of Chimera usage and features",
                                          justify="left",
                                          variable=self.usersVar)
	self.usersChk.pack(side=Tk.LEFT, pady=2)
	usersFrame.pack(side=Tk.TOP, fill=Tk.X)
	entries.append(self.usersVar)
        ############################

        ## for chimera-announce mailing list
        announceFrame = Tk.Frame(self.entryFrame)
        self.announceVar = Tk.IntVar(parent)

	lab = Tk.Label(announceFrame, width=2, text='')
	lab.pack(side=Tk.LEFT)
	self.announceChk = Tk.Checkbutton(announceFrame,
                                          text="Add me to the Chimera announcements mailing list (chimera-announce@cgl.ucsf.edu),\n" \
                                          "which is used for announcing new releases and workshops " \
					  "(~2-3 messages per year)",
                                          justify="left",
                                          variable=self.announceVar)
	self.announceChk.pack(side=Tk.LEFT, pady=2)
	announceFrame.pack(side=Tk.TOP, fill=Tk.X)
	self.announceVar.set(1)
	entries.append(self.announceVar)
        ############################

	self.entryFrame.pack(side=Tk.TOP, fill=Tk.X, pady=4)
	return entries

    def checkEntries(self, user=None, email=None, **kw):
	##check if name is in valid format
	if user == '' or not ',' in user:
	    replyobj.error("Please re-enter Name in the form 'Last, First'.\n")
	    return False

	##check that they've entered a valid email address
	if email == '' or not ('@' in email):
	    replyobj.error("Please enter a valid email address.\n")
	    return False

	return True

    def checkResponse(self, text):
	##What message has the server returned...?

	if text.find('from chimera import registration') >= 0:
	    return 'OK'
	if text.find('mailto:chimera-bugs@cgl.ucsf.edu') >= 0 or text.find("Internal Server Error") >= 0:
	    return 'Error'
	if text.find(' is unacceptable.') >= 0:
	    return 'Invalid'
	return 'Unknown'

    def processResponse(self, res, text):
	if res == 'Invalid':
	    start = text.find('submitted')
	    end   = text.find('is unacceptable')

	    ##extract the part of the message that specifies what's wrong
	    error = text[start+10:end-1]

	    replyobj.error("The %s you have entered is not valid. Please try again.\n" % error)
            return 0
            
	elif res == 'Error':
            from BugReport import bugNotify
            bugNotify("An error has occurred on the Chimera registration server.",
                      "Encountered an error in the server-side " \
                      "registration script."
                      )
            return 0

	elif res == 'OK':
	    start = text.find("\"\"\"") + 3
	    end = text.rfind("\"\"\"")
	    ##just extract the registration certificate
	    msg = text[start:end]

	    from chimera import registration
	    data = registration.install(msg)

	    ##result of installation procedure
	    res = data[1]

	    if data[0] == 0:
		res = "Installation Error: " + res + '\n'
		replyobj.error(res)
                return 0
	    else:
		replyobj.info(res + '\n')
		self.status("Thank you for registering chimera.\n",
			echoToMain=True)
                return 1

    def Register(self):
	info = {
	    'user': self.entries[0].get().encode('utf8'),
	    'email': self.entries[1].get().encode('utf8'),
	    'organization': self.entries[2].get().encode('utf8'),
	    'type': self.entries[3].get(),
	    'usage' : self.entries[4].get(),
	    'nih': self.entries[5].get()
           }

        doSubscribeUsers = self.entries[6].get()
        doSubscribeAnnounce = self.entries[7].get()
        
	##for 'backwards compatibility' with existing registration scheme:
	if info['nih']:
	    info['nih'] = 'yes'
	else:
	    info['nih'] = ''

	if not self.checkEntries(**info):
	    return

	self.status("Contacting cgl.ucsf.edu...\n")

	# import urllib
	info.update({ 'action': 'Register automatically' })
	params = urllib.urlencode(info)
	file = urllib.urlopen(regURL, params)
	text = file.read()

	res = self.checkResponse(text)
	ok = self.processResponse(res, text)
	if res != 'Invalid':
	    self.Close()

            ## everything went OK on the server-side
            if ok:

                msgs = []
                
                ## if they wanted to subscribe to the mailing list
                if doSubscribeUsers:
                    try:
                        self.subscribe(usersURL, info['user'], info['email'])
                    except:
                        msgs.append(SubscribeFailure % "discussion")
                    else:
                        msgs.append(SubscribeOkay % ("discussion",
							    info['email']))
                if doSubscribeAnnounce:
                    try:
                        self.subscribe(announceURL, info['user'], info['email'])
                    except:
                        msgs.append(SubscribeFailure % "announcements")
                    else:
                        msgs.append(SubscribeOkay % ("announcements",
							    info['email']))

                ## pop up the dialog that says Chimera has been
                ## registered
                AlreadyRegisteredDialog("\n".join(msgs))

    def subscribe(self, url, username, email):
        param_dict = {
            'email'    : email,
            'fullname' : username
            }
	params = urllib.urlencode(param_dict)
	file = urllib.urlopen(url, params)
	text = file.read()
        print "GOT %s for text" % text
            

import dialogs
dialogs.register(RegDialog.name, RegDialog)


class AlreadyRegisteredDialog(ModelessDialog):
    title = "Registered"
    buttons = ('OK')
    highlight = 'OK'

    def __init__(self, addl_info=None):

        self.addl_info = addl_info
        
        ModelessDialog.__init__(self, oneshot=1)

    def fillInUI(self, parent):
        from chimera.HtmlText import HtmlText

        t = HtmlText(parent, width=60, height=7, relief='flat', wrap='word')
        t.insert(0.0 , "<p>Your copy of Chimera has been registered...." \
                 "thank you!</p>"
                     )
        t.grid(row=0, column=0, sticky="nsew")

        if self.addl_info:
            t.insert(0.0, "<p>%s</p>" % self.addl_info)

        t.configure(state='disabled')
        
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(0, weight=1)
