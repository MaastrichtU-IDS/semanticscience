import chimera
from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw, os.path, string
from chimera import HtmlText

##-------------------------
# This is the graphical interface for locally searching Chimera's documentation.
# The Chimera documentation website has a search box, but this requires that the
# user has a web connection. Because we bundle the Chimera documentation locally
# within the distribition, it makes sense to be able to search it locally as well.
# This dialog provides that functionality. 
# 
# In order to [quickly] search through any data, you must use some mechanism
# that can index the data and then search the index for desired terms.
# We use a third-party package called 'swish-e' to handle this functionality.
# swish-e is freely available (http://swish-e.org/) and compiles on all
# Chimera-supported platforms. It is distributed as  a command line tool.
# There are actually two parts to achieving this search functionality:
#
# 1. Indexing
# Before you can search a tree of documents (such as the Chimera documentation), you must
# first index the data. This produces some specially-formatted index file that can then 
# be used to quickly search for desired terms. This indexing step is handled by the swish-e
# executable, during the Chimera build process.
# Chimera/docs/GNUmakefule has a build_index target that invokes the swish-e executable
# and passes it a configuration file (checked in to CVS at chimera/docs/swish-e.conf).
# This file has all the information about what should / should not be indexed, where to
# write out the index file (chimera/docs/chimera-doc.idx), and other information needed
# by swish-e to properly index the chimera documentation tree. The result of indexing
# is an index file (chimera-doc.idx) that is subsequently used when performing a search query.
#
#
# 2. Searching
# Step 1 (Indexing) is just a prereq. to be able to actually search the documentation. This
# is accomplished not by  invoking the swish-e exectuable directly, but by using yet another
# third party package (confusingly called SwishE - http://jibe.freeshell.org/bits/SwishE/)
# which serves as a Python wrapper around
# the swish-e functionality. When compiled, this package produces a .so called SwishE.so
# that is copied into Chimera's Python's site-packages directory. This library depends on the
# libswish-e.so library provided by the swish-e package.
# Note that the swish-e command line executable is *not* actually distributed with Chimera
# (it is only used during the Chimera build phase to perform indexing) -
# only the SwishE.so library and the libswish-e.so that it depends on are included in the
# distribution (and the index file that is actually used to search against).
# This is all that is needed to provide search functionality from within Chimera.
#
#
# Performing a search from within Chimera.
# 
# Here's basically what happens when the user wants to search the local documentation from
# within Chimera.
#
# * They go to Help->Search Documentation
#
# * This instantiates the SearchDialog class below. An entry field on the left side of the 
#   window can be used to enter search terms. The right side of the window displays results.
#
# * The SearchDialog class has a Searcher object (see documentation below) that handles the
#   actual search side of things.
#
# * SearchDialog invokes a method of it's Searcher object to obtain search results from the
#   Chimera documentation tree
#
# * The right-hand side of the SearchDialog window is an HtmlText widget. Once results from
#   a search are returned, this widget (containing the previous search's results), is cleared
#   and the new search's results are formatted in html and displayed in this widget. Each
#   search result shows up as a link, and clicking on any link will invoke code to show the
#   desired search result in a web browser. The file displayed in the browser is actually 
#   the locally installed version of the documentation page, and not the one on the web.
#
#



class SearchDialog(ModelessDialog):

    buttons = ('Close')
    name    = "Search Documentation"
    help    = "UsersGuide/menu.html#localsearch"
    
    def __init__(self):

        self.doc_searcher = Searcher()

        ModelessDialog.__init__(self)


    def fillInUI(self, parent):
        
        self.searchFrame   = Tkinter.Frame(parent)
        self.resultsFrame  = Tkinter.Frame(parent)

        placeHolder = Tkinter.Frame(parent,borderwidth=2,relief='groove')
        Tkinter.Frame(placeHolder).grid(row=0,column=0,sticky='nsew')
        
        self.searchFrame.grid(row=0,column=0,pady=10, sticky='nsew')
        placeHolder.grid(row=0,column=1,sticky='nsew')
        self.resultsFrame.grid(row=0,column=2, pady=10, sticky='nsew')
        #self.resultsFrame.pack(side='right', pady=10, expand=True, fill='y')
        #placeHolder.pack(side='right', expand=True, fill='y')
        #self.searchFrame.pack(side='right', pady=10, expand=True, fill='y')
        
        parent.rowconfigure(0,weight=1)
        parent.columnconfigure(2,weight=1)


        self.createSearchPanel(self.searchFrame)
        #parent.columnconfigure(2,weight=1)
        self.createResultsPanel(self.resultsFrame)

    def createSearchPanel(self, parent):
        #self.searchFrame = Tkinter.Frame(parent)
        #self.searchFrame.grid(row=0,column=0,sticky='nsew')
        #parent.rowconfigure(0,weight=1)
        #parent.columnconfigure(0,weight=1)

        exp_label = """<font size="+5">Chimera documentation search</font>
<pre>Enter one or more terms; combinations can be indicated 
with the <b>and</b>, <b>or</b>, <b>not</b>, and parentheses operators
(<b>and</b> is implicit if no operators are specified). 

Example: <i>select command not tutorial</i></pre>"""
        
        ## search instructions - row 0
        exp_text  = HtmlText.HtmlText(parent,
                                      relief="flat",
                                      height=11, width=50,
				      highlightthickness=0)
        exp_text.insert(0.0, exp_label)
        exp_text.configure(state='disabled')
        exp_text.grid(row=0,column=0,columnspan=2,padx=10,sticky='new')
        
        #exp_label = Tkinter.Label(parent, text=exp_text)
        #exp_label.grid(row=0,column=0,columnspan=2)

         ## search button and entry - row 1
        self.search_button = Tkinter.Button(parent, text="Search",
                                            command = self.search)
        self.search_button.grid(row=1,column=0, padx=5, sticky='nw')  ## south too?

        self.search_entry = Tkinter.Entry(parent, width=30)
        self.search_entry.bind("<Return>",self.search)
        self.search_entry.grid(row=1,column=1, padx=5, sticky='nw')

        #self.makeAdvComponents(self, parent)
        #self.createAdvPanel(parent)
        parent.rowconfigure(1,weight=1)
        parent.columnconfigure(1,weight=1)

    def makeAdvComponents(self, parent):
        ## advanced checkbutton - row 2
        self.advanced_var = Tkinter.IntVar(False)
        self.advanced_checkb = Tkinter.Checkbutton(parent,
                                                   var = self.advanced_var,
                                                   command = self.doAdvanced,
                                                   text = "Advanced options")
        self.advanced_checkb.grid(row=2,column=0,sticky='nw',pady=10, columnspan=2)

        parent.rowconfigure(3, weight=10)
        parent.rowconfigure(2, weight=5)
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=20)
        
    def createAdvPanel(self, parent):
        self.advancedFrame = Tkinter.Frame(parent)
        self.advancedFrame.rowconfigure(0,weight=1)
        self.advancedFrame.columnconfigure(0,weight=1)
        
        self.restrict_label1 = Tkinter.Label(self.advancedFrame, text=\
                                             "Restrict search (leave blank to search everything):")
        self.restrict_label1.grid(row=0,column=0,columnspan=2,sticky='w')

        self.title_var    = Tkinter.IntVar(False)
        self.title_checkb = Tkinter.Checkbutton(self.advancedFrame,
                                                var = self.title_var,
                                                text = "Title tags")
        self.heading_var    = Tkinter.IntVar(False)
        self.heading_checkb = Tkinter.Checkbutton(self.advancedFrame,
                                                  var = self.heading_var,
                                                  text = "Heading tags")

        self.comment_var    = Tkinter.IntVar(False)
        self.comment_checkb = Tkinter.Checkbutton(self.advancedFrame,
                                                  var = self.comment_var,
                                                  text = "Comment tags")

        self.emph_var    = Tkinter.IntVar(False)
        self.emph_checkb = Tkinter.Checkbutton(self.advancedFrame,
                                               var = self.emph_var,
                                               text = "Emphasized text")

        self.title_checkb.grid(row=1,column=0,sticky='w')
        self.heading_checkb.grid(row=2, column=0,sticky='w')
        self.comment_checkb.grid(row=1,column=1,sticky='w')
        self.emph_checkb.grid(row=2,column=1,sticky='w')

        #self.max_label = Tkinter.Label(self.advancedFrame, text="Max. number of results")
        #self.max_label.grid(row=3,column=0,pady=15)
        self.max_combo = Pmw.ComboBox(self.advancedFrame, labelpos = 'w',
                                      labelmargin = 10,
                                      label_text = "Max. # of results",
                                      dropdown=1
                                      )
        self.max_combo.setlist(["No Limit","10","50","100"])
                                     
        
        self.max_combo.grid(row=3,column=0,columnspan=2,sticky='w',pady=20)


        #self.advancedFrame.rowconfigure(0,weight=1)
        #self.advancedFrame.rowconfigure(1,weight=1)
        #self.advancedFrame.rowconfigure(2,weight=1)
        self.advancedFrame.columnconfigure(0,weight=1)
        self.advancedFrame.columnconfigure(1,weight=5)
        
    def createResultsPanel(self, resFrame):
        res_title = Tkinter.Label(resFrame, text="Search Results:")
        res_title.grid(row=0,column=0,sticky='nw',padx=15,pady=10)

        self.res_text = Pmw.ScrolledText(resFrame,
                                         text_pyclass = HtmlText.HtmlText,
                                         text_relief = 'flat',
                                         text_wrap = 'word',
                                         text_height=15, ## comment out
                                         text_width=50
                                         )
        self.res_text.grid(row=1,column=0, sticky='nsew')
        self.res_text.configure(text_state='disabled')

        resFrame.rowconfigure(1,weight=1)
        resFrame.columnconfigure(0,weight=1)
        
    def doAdvanced(self):
        if self.advanced_var.get():
            self.advancedFrame.grid(row=3,column=0,columnspan=2,sticky='new')
        else:
            self.advancedFrame.grid_forget()

    def search(self, event=None):
        query = self.search_entry.get()
        res = self.doc_searcher.doSearch(query)
        res_str = self.doc_searcher.formatResults(res)

        self.res_text.configure(text_state='normal')
        self.res_text.clear()
        self.res_text.component('text').reinitialize()
        self.res_text.insert(0.0, res_str)
        self.res_text.configure(text_state='disabled')

chimera.dialogs.register(SearchDialog.name, SearchDialog)

##--------------------------------------
# The Searcher class performs all the hard work of actually searching the Chimera documentation
# tree.
#
# It creates a SwishE object (from the SwishE.so library provided by the SwishE package).
# The SwishE object is created with the path to the index file (created during the Chimera
# build phase), which it uses to actually search for the query terms. This index file 
# is located in the Chimera distribution at CHIMERA/libs/chimera/helpdir/chimera-docs.idx .
#
# When a search is initiated, 'doSearch' method of the Searcher object is called with the
# search query, and this returns a results object. The results object is then formatted into
# html with the 'formatResults' method, and eventually displayed on the right hand side
# of the SearchDialog window. More information about the SwishE class and the search results
# object can be found within the SwishE documentation. 
#
# Each results link has a callback function associated with it - this is
# what actually gets called with the link is clicked on. The function for each link is
# chimera.help.display , which uses Chimera's online help mechanism to display the appropriate
# page.
#

        
class Searcher:
    def __init__(self):
        from chimera import pathFinder
        import os.path
        import SwishE

        pf = pathFinder()
        data_root = pf.dataRoot
        idx_file = os.path.join(data_root,"chimera","helpdir","chimera-docs.idx")
        self.index = idx_file
        self.index = self.index.replace("\\","/")

        self.swisher = SwishE.new(repr(self.index))

    def doSearch(self, query):
        search = self.swisher.search('')

        results = search.execute(query)

        return results

    
    def formatResults(self, results):
        if results.hits() == 0:
            return "<i>Your search did not return any results</i>"

        results_str = "<ol>"
        for r in results:
            try:
                doc_title = r.getproperty('swishtitle')
            except:
                doc_title = "(Title unavailable)"

            doc_path = r.getproperty('swishdocpath')
            #print "here is ", doc_path
            c = doc_path.split('/')
            #print "c is ", c
            doc_path = string.join(c[1:],'/')
            #print "now is ", doc_path

            results_str += "<li><a href=\"python:chimera.help.display('%s')\">%s</a></li>" % \
                           (doc_path, doc_title)

        results_str += "</ol>"

        return results_str
