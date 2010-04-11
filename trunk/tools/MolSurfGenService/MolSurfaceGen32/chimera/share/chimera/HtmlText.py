# This file defines a class called 'HtmlText', which can be used just like
# a Tkinter.Text widget, except it will parse it's input as HTML and render
# the output appropriately (e.g. links, font size, color, style, etc.)
#
# The HtmlText widget supports the following tags:
#
# 1. Links <a href="">
#    Three different protocols are supported  by the <a> tag:
#       http:    - designates that link should open a web page
#       https:   - designates that link should open a web page
#       command: - designataes that link should be executed as a command
#       python:  - designates that link should be executed as python code
#
#    So if you wanted a link that executed the Chimera command 'open 1gcn',
#    the HTML tag would look like this:
#       <a href="command:open 1gcn">Open model 1gcn</a>
#
#    Links appear as blue underlined text (as they do in web browsers), and
#    the mouse changes shape (to a pointing hand) when a link is moused over.
#
#    'http:' and 'https:' protocol links are handled by using Python's
#    webbrowser library, calling webbrowser.open with link target (which is
#    assumed to be an url)
#
#    'command:' protocol links are handled by calling midas_text.makeCommand
#    with the link target (which is assumed to be a valid Chimera command)
#
#    'python:' protocol links are handled using the built in 'exec' command
#    with the link target (which is assumed to be valid python code).  Because
#    of the contents the extent of Python code that can be used as a link
#    target is more or less limited to statments that don't require any
#    indentation; multiple statements could be included by seperating them
#    with semicolons.
#
#
# 2. Ordered lists <ol> and Unordered lists <ul>
#    These tags have sufficient support, with the exception that if a list
#    item spans multiple lines, all lines after the first will not be
#    indented, but will be flush with the item number (in ordered lists) or
#    '*' (in unordered lists)
#
# 3. Preformatted text <pre>
#    This tag is fully supported. a blank line is inserted before and after
#    the text within the <pre> tags, and all the whitespace in the text within
#    the <pre> tags is conserved
#
# 4. Paragraph <p>
#    self-explanatory
#
# 5. Bold <b>
#    self-explanatory
#
# 6. Italics <i>
#    self-explanatory
#
# 7. Underline <u>
#    self-explanatory
#
# 8. Line break <br>
#    self-explanatory
#
# 9. Font attributes <font size="" color="">
#    Size can be specified either as an absolute number (possibly represents
#    pixels), or as a number preceded by a '+' or '-' sign, which means n
#    (pixels?) larger than or smaller than (respectively) the current font
#    size.
#
#    Color can be specified either as any of the Tkinter-supported color
#    names, or 12-digit hexadecimal numbers preceded by a '#' (e.g., <font
#    color="#b8b886860b0b">)
#
# -=-=-=-=-=-=-=-=-=-=-=--=
#
# There are many classes in this file, which are all needed to conform to
# Python's SGML parser API, as documented in the Python library
#
#    http://www.python.org/doc/current/lib/module-htmllib.html
#
# An instance of HtmlText class contains instances of the following classes:
#
#    Html2TkParser
#       This class actually parses the html tags in the input text, but
#       doesn't write any output (this is the job for the Writer). The 'feed'
#       method of this class is called when text is inserted into the HtmlText
#       widget (via the 'insert' method). Html2TkParser class has several
#       methods named somthing like 'start_TAG' or 'end_TAG' where TAG is
#       actually the name of an html tag  (such as 'start_a' and 'end_a').
#       These methods are called when a tag is opened or closed, respectively.
#
#    Html2TkFormatter
#       The formatter is kind of like a state machine that keeps track of what
#       tags the parser is currently "in". For example, if you have HTML that
#       looks like
#          <font color="green"><b>Hello</b> world </font>
#       The formatter would need to know that 'Hello' should be green and bold,
#       while 'world' should only be green.
#
#
#    Writer
#       The Writer actually performs the task of converting the semantics of
#       the HTML tags to their Tkinter-equivalent and writing this
#       appropriately-formatted output to the HtmlText widget.
#
#    HyperlinkManager
#       Maintains information about all the links ( <a> tags ) that are
#       currently displayed in the HtmlText widget. It is necessary to
#       maintain this information s.t. clicking on elicits the correct
#       behavior (i.e. the right action on the right target).  Thus, for each
#       link, the HyperlinkManager records what type of link it is (http:,
#       https:, command:, or python:), tracks the link's corrensponding
#       Tkinter.Text 'tag' name, and also is responsible for rendering a
#       context menu with the appropriate menu items when that link is
#       right-clicked on.
#
#
#
#
# Inserting plain text into an HtmlText widget
# -=-=--=-=-=-=--=-=-=-=-=-=-=--=-=-=-=-=-=-=-=
#
# In some cases, it is desirable to programmatically insert text into an HTML
# widget which you would like to be interpreted as plain text and not html
# (e.g., text that has a lot of '<' '>' and '&' characters in it (which you
# *could* escape as &lt;, &gt;, and &amp;, respectively).
#
# Of course, (assuming you have an instance of an HtmlText object called
# 'htmltext') you can't just say
#
#   htmltext.insert(0.0, "a < b <= c")
#
# because the widget will attempt to parse this text as Html. Instead, you
# must use the 'insert' method of HtmlText's superclass (Tkinter.Text):
#
#   Tkinter.Text.insert(htmltext, 0.0, "a < b <= c" )


import Tkinter, Pmw
from Tkinter import END
import htmllib
import formatter, string
from Midas import midas_text, midas_ui
import chimera

def exec_code(code):
    import chimera
    exec(code)

def webbrowser_wrapper(url):
    # use help module to centralize error recovery
    import help
    help.display(url)


URL    = "URL"
CMD    = "command"
PYCODE = "Python code"

LINK_FNS = {
    URL   : webbrowser_wrapper,
    CMD   : midas_text.makeCommand,
    PYCODE: exec_code
    }

class HtmlParseError(Exception):
    pass

class Html2TkParser(htmllib.HTMLParser):

    def __init__(self, f):
        self.formatter = f
        self.writer = f.writer
        self.hlink = self.writer.text_obj.hlink

        htmllib.HTMLParser.__init__(self, f, True)

    def start_font(self, attrs):
        color = None
        size =  None

        new_style = {'color': None,
                     'size': None
                     }

        for attrname, value in attrs:
            value = value.strip()

            if attrname == 'color':
                new_style['color'] = str(value.strip())
            elif attrname == 'size':
                new_style['size']  = str(value.strip())

        for key, value in new_style.items():
            if not value:
                del new_style[key]


        self.formatter.push_style(new_style)


    def end_font(self):
        self.formatter.pop_style()


    def start_u(self, attrs):
        self.formatter.push_style( {'underline': True} )

    def end_u(self):
        self.formatter.pop_style()


    def start_a(self, attrs):
        link_info = {}

        for k in ('href', 'title'):
            link_info[k] = None

        for attrname, value in attrs:
            value = value.strip()

            if link_info.has_key(attrname):
                link_info[attrname] = value

        self.anchor_bgn(link_info)


    def anchor_bgn(self, link_info):
        self.save_bgn()

        self.anchor = link_info['href']
        self.title  = link_info['title']


    def anchor_end(self):
        raw_text = self.save_end()
        text = string.strip(raw_text)

        #if not self.formatter.nospace:   HAAAACK
        self.writer.send_literal_data(" ")

        ## link text, target, function
        if self.anchor:
            ## make a link object here....
            l = Link(text, self.anchor, self.title)
            if l.getType() and l.getTarget():
                t = self.hlink.add(l)
            else:
                t = None
        else:
            t = None

        ## NEED to mirror what formatter does here to maintain its state...
        self.formatter.hard_break = raw_text[-1:] == '\n'
        self.formatter.nospace = self.formatter.para_end = self.formatter.softspace = \
                                 self.formatter.parskip = self.formatter.have_label = 0
        ## OK
        if t:
            self.writer.send_literal_data(text, useTags=list(t))
        else:
            self.writer.send_literal_data(text)

        self.writer.atbreak = True

        if self.anchor and text:
            self.anchor = None
        if self.title and text:
            self.title  = None

    def convert_charref(self, name):
        try:
	    n = int(name)
	    if n < 128:
		    return chr(n)
            return unichr(n)
        except ValueError:
            return

    def convert_entityref(self, name):
        from htmlentitydefs import name2codepoint
        if name in name2codepoint:
            n = name2codepoint[name]
	    if n < 128:
		    return chr(n)
            return unichr(n)
        else:
            return

class Html2TkFormatter(formatter.AbstractFormatter):

    def _reinitialize(self):
        self.align = None               # Current alignment
        self.align_stack = []           # Alignment stack
        self.font_stack = []            # Font state
        self.margin_stack = []          # Margin state
        self.spacing = None             # Vertical spacing state
        self.style_stack = []           # Other state, e.g. color
        self.nospace = 1                # Should leading space be suppressed
        self.softspace = 0              # Should a space be inserted
        self.para_end = 1               # Just ended a paragraph
        self.parskip = 0                # Skipped space between paragraphs?
        self.hard_break = 1             # Have a hard break
        self.have_label = 0

class HtmlText(Tkinter.Text):

    def __init__(self, master=None, cnf={}, **kw):

        Tkinter.Text.__init__(self, master, cnf, **kw)

        self.hlink     = HyperlinkManager(self)
        self.writer    = Writer(self)
        self.formatter = Html2TkFormatter(self.writer)
        self.parser    = Html2TkParser(self.formatter)


    def insert(self, index, chars, *args):
        self.parser.feed(chars)

    def reinitialize(self):
        self.writer._reinitialize()
        self.formatter._reinitialize()
        self.tag_delete(*[t for t in self.tag_names() if not t=='hyper'])
        self.parser.reset()

class Link:
    def __init__(self, text, target, title):
        self.text   = text
        self.title  = title

        self.link_type, self.target = self.determineType(target)

    def determineType(self, target):
        link_type = None
        link_targ = None

        try:
            protocol, data = target.split(":", 1)
        except ValueError:
            pass
        else:
            if protocol in ('http', 'https'):
                link_type = URL
                link_targ = target
            elif protocol == 'command':
                link_type = CMD
                link_targ = data
            elif protocol == 'python':
                link_type = PYCODE
                link_targ = data

        return link_type, link_targ

    def getText(self):
        return self.text

    def getTarget(self):
        return self.target

    def getTitle(self):
        return self.title

    def getType(self):
        return self.link_type

class HyperlinkManager:

    def __init__(self, text):

        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.text.tag_bind("hyper", "<Button-3>", self._showMenu)

        self.reset()

    def reset(self):
        self.links = {}


    def add(self, link): #txt, target, title, type):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = link

        if link.getType() == URL and (not link.getTitle()):
            balloon_txt = link.getTarget()
        else:
            balloon_txt = link.getTitle()

        if balloon_txt:
            balloon=Pmw.Balloon(initwait=1000, state="balloon")
            balloon.tagbind(self.text, tag, balloon_txt)

        return "hyper", tag

    def _enter(self, event):
        self.text.configure(cursor="hand2")

    def _showMenu(self, event):
        tag_name = [t for t in self.text.tag_names(Tkinter.CURRENT) if t[:6]=='hyper-']
        if not tag_name: return
        else: tag_name = tag_name[0]

        a_link =  self.links[tag_name]
        link_title = a_link.getTitle()
        link_txt   = a_link.getText()
        link_targ  = a_link.getTarget()
        link_type  = a_link.getType()

        menu = Tkinter.Menu(self.text, tearoff=False)

        if link_title:
            menu.add_command(label="Show description in reply log",
                     command = lambda: chimera.replyobj.status(
                             "%s\n" % link_title, log=True, blankAfter=10)
                     )

        if link_type in (CMD, PYCODE):
	    show_label = "code"
        else:
	    show_label = "URL"
        menu.add_command(label="Show %s in reply log" % show_label,
                     command = lambda: chimera.replyobj.status(
                            "%s\n" % link_tag, log=True, blankAfter=10)
                     )
        if link_type == URL:
	    action = "Open"
	    subject = "URL"
        else:
	    action = "Execute"
	    subject = "code"
        menu.add_command(label="%s %s" % (action, subject),
                         command = lambda: LINK_FNS[link_type](link_targ)
                         )

        if link_type==CMD and midas_ui.uiActive:
            cmd_line = midas_ui.ui.cmd.component('entryfield')
            menu.add_command(label   = "Paste into command line",
                             command = lambda: cmd_line.setentry(link_targ)
                             )

        menu.tk_popup(event.x_root, event.y_root, entry='')


    def _leave(self, event):
        self.text.configure(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(Tkinter.CURRENT):
            if tag[:6] == "hyper-":
                type   = self.links[tag].getType()
                fn     = LINK_FNS[type]
                target = self.links[tag].getTarget()
                try:
                    fn(target)
                except IOError:
                    pass
                return



class TagManager:
    def __init__(self):
        self.tag_count = 0
        self.template = "tag"

    def newTag(self):
        self.tag_count += 1
        return "%s-%d" % (self.template, self.tag_count)

    def reset(self):
        self.tag_count = 0

    def forgetLastTag(self):
        self.tag_count -= 1


class Writer(formatter.NullWriter):

    def __init__(self, text_obj):
        formatter.NullWriter.__init__(self)

        self.text_obj = text_obj

        self._reinitialize()

        font = self.text_obj.cget('font')
        if not font:
            font = 'Helvetica -12'
        font = self.text_obj.master.tk.call('font', 'actual', font)

        font = list(font)
        self.text_size = int(font[font.index("-size")+1])
        self.size = None

        self.text_font = tuple(font)

    def _reinitialize(self):
        self.tag = ""
        self.margin = 5
        self.cur_indent = ""
        self.col = 0
        self.bold = self.italic = self.underline = 0
        self.color = None
        self.fonts = []

        self.atbreak = False

        self.tm = TagManager()

    def reset(self):
        self.col = 0
        self.atbreak = False

    def _getNewFont(self, font, **kw):
        font = list(font)

        for k in kw.keys():
            try:
                key_idx = font.index("-" + k)+1
                font[key_idx] = kw[k]
            except ValueError:
                pass

        return tuple(font)

    def send_hor_rule(self, *args, **kw):
        ## TODO: need to know how to determine the width
        ## of the text object, use 20 for now

        Tkinter.Text.insert(self.text_obj, END, "\n" + u"\u2015" * 20 + "\n")
        self.col     = 0
        self.atbreak = False

    def new_margin(self, tag, indent):

        if indent==0:
            self.cur_indent = ""
        else:
            self.cur_indent = " " * self.margin * indent


    def send_label_data(self, label):
        #print "in send_label_data: %s" % label
        self.col = self.col + self.do_indent()
        Tkinter.Text.insert(self.text_obj, END, label)
        self.atbreak = True
        self.col = self.col + len(label)


    def new_font(self, font):
        #print "new font called: ", font

        if font is None:
            self.tag = ''
            self.italic = self.bold = 0
        else:
            tag, italic, bold, typewriter = font

            self.tag = tag
            self.italic = italic
            self.bold = bold

    def new_styles(self, styles):
        if len(styles) == 0:
            self.color     = None
            self.underline = 0
            self.size      = None

        else:
            style_list = list(styles)
            style_list.reverse()

            found_color = found_underline = found_size = False

            for s in style_list:
                if s.has_key('color') and not found_color:
                    self.color = s['color']
                    found_color = True
                if s.has_key('underline') and not found_underline:
                    self.underline = 1
                    found_underline = True
                if s.has_key('size') and not found_size:
                    self.size = s['size']
                    found_size = True

            if not found_color:     self.color      = None
            if not found_underline: self.underline  = 0
            if not found_size:      self.size       = None

    def send_line_break(self):
        #print "send_line_break called"

        Tkinter.Text.insert(self.text_obj, END, "\n")

        self.atbreak = False
        self.col = 0

    def send_paragraph(self, blankline):
        #print "send_paragraph called with blankline: %s" % blankline

        Tkinter.Text.insert(self.text_obj, END, "\n"*blankline)

        self.col = 0
        self.atbreak = False


    def _applyTag(self, tag_name):

        working_font = self.text_font[:]
        used_tag = False

        ## add any Tkinter tags, as necessary...
        if self.tag in ("h1", "h2", "h3"):
            working_font = self._getNewFont(working_font, size=16, weight="bold")
            used_tag = True

        if self.bold:
            working_font = self._getNewFont(working_font, weight="bold")
            used_tag = True

        if self.italic:
            working_font = self._getNewFont(working_font, slant="italic")
            used_tag = True

        if self.underline:
            working_font = self._getNewFont(working_font, underline=1)
            used_tag = True

        if self.size:
            use_size = None

            if self.size[0] == "+":
                use_size = self.text_size + \
                           int(self.size[1:])
            elif self.size[0] == "-":
                use_size = self.text_size - \
                           int(self.size[1:])
            else:
                use_size = int(self.size)

            working_font = self._getNewFont(working_font, size=use_size)
            used_tag = True

        if used_tag:
            self.text_obj.tag_configure(tag_name, font=working_font)


        if self.color:
            try:
                self.text_obj.tag_configure(tag_name, foreground=self.color)
            except Tkinter.TclError, what:
                raise HtmlParseError, what
            #finally: ## not sure about this...
            used_tag = True

        if not used_tag:
            self.text_obj.tag_delete(tag_name)
            self.tm.forgetLastTag()

    def do_indent(self):
        Tkinter.Text.insert(self.text_obj, END, self.cur_indent) ## not sure here...
        return len(self.cur_indent)            ## not sure here...

    def insert_space(self):
        t = self.tm.newTag()
        Tkinter.Text.insert(self.text_obj, END, " ", t)
        self._applyTag(t)


    def send_flowing_data(self, data, useTags=None):
        #print "sfd: **%s**  len==%d" % (data, len(data))
        try:
            punc = (data.lstrip())[0] in '!"#$%&\'*+,-./:;<=>?@\\^_`|~'
        except IndexError:
            punc=False

        if not data:
            return

        atbreak = self.atbreak or data[0].isspace()

        if punc:
            atbreak = False

        col = self.col
        insert = Tkinter.Text.insert

        ######
        #if not self.line_label:
        #    i = self.do_indent()
        #    self.col = self.col + i
        ######

        for word in string.split(data):
            taglist = []

            if atbreak:
                self.insert_space()
                col = col + 1

            t = self.tm.newTag()
            taglist.append(t)
            if useTags:
                taglist = taglist + useTags

            insert(self.text_obj, END, word, tuple(taglist))
            col = col + len(word)
            atbreak = True

            self._applyTag(t)

        self.col = col
        self.atbreak = data[-1].isspace()


    def send_literal_data(self, data, useTags=None):
        #print "sld: **%s**" % data

        taglist = []
        t = self.tm.newTag()
        taglist.append(t)
        if useTags:
            taglist = taglist + useTags

        Tkinter.Text.insert(self.text_obj, END, data, tuple(taglist))

        self._applyTag(t)

        i = data.rfind('\n')
        if i >= 0:
            self.col = 0
            data = data[i+1:]
        data = data.expandtabs()
        self.col = self.col + len(data)
        self.atbreak = False
