from gi.repository import Gtk, GObject

import subprocess, re, os, traceback
from threading import Thread

from GrepEngine import GrepEngine, NoResultsException, GrepException, BadRegexException
import Path

# This is a scrolledWindow subclass. We add it directly to the notebook in the
# main window. We subclass it to add helper/convenience functions.
class VizigrepTab(Gtk.ScrolledWindow):
    def __init__(self, app, notebook):
        Gtk.ScrolledWindow.__init__(self)
        self.app = app
        self.notebook = notebook
        self.results = None
        self.isSearching = False
        
        newTextView = Gtk.TextView()
        self.createTags(newTextView.get_buffer())
        self.add(newTextView)
        self.notebook.append_page(self)
        
        # Construct tab label and hidden spinner
        box = Gtk.Box(Gtk.Orientation.HORIZONTAL, spacing=6)
        self.label = Gtk.Label('[New tab]')
        self.spinner = Gtk.Spinner()
        self.notebook.set_tab_label(self, box)
        box.pack_start(self.label, True, True, 0)
        box.pack_start(self.spinner, True, True, 0)
        box.get_children()[0].show() # Always show label
        
        self.ge = GrepEngine()
    
    def getIndex(self):
        return self.notebook.page_num(self)
    
    def getTextView(self):
        return self.get_child()
    
    def getTextBuffer(self):
        return self.get_child().get_buffer()
        
    def setTitleText(self, text):
        self.label.set_text(text)
        
    def setSpinner(self, active):
        if active:
            self.spinner.show()
            self.spinner.start()
        else:
            self.spinner.stop()
            self.spinner.hide()

    def createTags(self, txtbuf):
        txtbuf.create_tag("fixed", family="Monospace")
        txtbuf.create_tag("link", foreground="Blue")
        txtbuf.create_tag("red", foreground="Red")
        txtbuf.create_tag("green", foreground="Dark Green")
        txtbuf.create_tag("bg1", background="#DDDDDD")
    
    def startSearch(self, searchString, path, caseSensitive, doneCallback):
        self.isSearching = True
        new_thread = Thread(target=self.grep_thread, args=(searchString, path, caseSensitive, doneCallback))
        new_thread.start()
    
    def grep_thread(self, searchString, path, caseSensitive, doneCallback):
        self.results = None
        ex = None
        try:
            self.results = self.ge.grep(searchString, path, self.app.prefs.get('match-limit'), caseSensitive)
        except Exception as e:
            ex = e
        
        GObject.idle_add(self.grep_thread_done, ex, caseSensitive)
        GObject.idle_add(doneCallback, self) # Call main window's callback
    
    def grep_thread_done(self, exception, caseSensitive):
        txtbuf = self.getTextBuffer()
        
        if self.ge.cancelled:
            txtbuf.set_text("The search was cancelled")
        elif self.results:
            try:
                self.set_results(caseSensitive)
            except Exception as e:
                print type(e)
                print traceback.format_exc()
        elif exception:
            if isinstance(exception, GrepException):
                txtbuf.set_text("Grep error: %s" % exception.output)
            elif isinstance(exception, NoResultsException):
                txtbuf.set_text("No results found")
            elif isinstance(exception, BadRegexException):
                txtbuf.set_text("Search string error: %s" % str(exception))
            else:
                txtbuf.set_text("Unexpected Error: " + str(exception))
                print type(exception)
                print traceback.format_exc()
        self.setSpinner(False)
        self.isSearching = False
    
    def set_results(self, caseSensitive):
        results = self.results
        
        txtbuf = self.getTextBuffer()
        tag_link = txtbuf.get_tag_table().lookup('link')
        tag_red = txtbuf.get_tag_table().lookup('red')
        tag_green = txtbuf.get_tag_table().lookup('green')
        tag_bg1 = txtbuf.get_tag_table().lookup('bg1')

        max_fnlen = results.max_fnlen()
        max_lnlen = results.max_lnlen()
        max_txtlen = results.max_txtlen()
        taglist = []
        rstr = ''
        
        # Figure out max line length
        max_linelen = max_fnlen + 1 + max_txtlen
        if (self.app.prefs.get('show-line-numbers')):
            max_linelen += max_lnlen + 1
        
        string = self.escape_regex_str(results.search_string)
        lineNum = 1
        for r in results:
            lineStartIdx = len(rstr)
            
            # File name
            taglist.append( (len(rstr), len(r.fn), tag_link) )
            rstr += r.fn
            
            # Spaces to pad out filename
            if max_fnlen > len(r.fn):
                rstr += ' '*(max_fnlen-len(r.fn))
            
            # : after filename
            rstr += ':'
        
            # Line number and : 
            if (self.app.prefs.get('show-line-numbers')):
                taglist.append( (len(rstr), len(r.linenum), tag_green) )
                rstr += r.linenum
                if max_lnlen > len(r.linenum):
                    rstr += " "*(max_lnlen-len(r.linenum))
                rstr += ':'
                
            if caseSensitive:
                m = re.search(string, r.str)
            else:
                m = re.search(string, r.str, re.IGNORECASE)
            
            # Line contents
            if(m and len(m.group()) > 0):
                matched_text = m.group()
                (prematch, match, postmatch) = r.str.partition(matched_text)
                rstr += prematch
                taglist.append( (len(rstr), len(matched_text), tag_red) )
                rstr += matched_text
                rstr += postmatch
            else:
                rstr += r.str
            
            # Spaces to pad out line contents
            if max_txtlen > len(r.str):
                rstr += ' '*(max_txtlen-len(r.str))
            
            rstr += '\n'
            
            # Add text background tag every other line
            lineLength = len(rstr) - lineStartIdx - 1
            if (self.app.prefs.get('alternate-row-color')):
                if (lineNum % 2 == 1):
                    taglist.append( (lineStartIdx, lineLength, tag_bg1) )
            lineNum+=1
            
        txtbuf.set_text(rstr)
        self.apply_tags(txtbuf, rstr, taglist)
    
    def escape_regex_str(self, regex):
        if '(' in regex:
            regex = regex.replace('(', '\\(')  # Escape (
        if ')' in regex:
            regex = regex.replace(')', '\\)')  # Escape )
        return regex
    
    def apply_tags(self, txtbuf, rstr, taglist):
        tag_fixed = txtbuf.get_tag_table().lookup('fixed')
        
        txtbuf.apply_tag(tag_fixed, txtbuf.get_start_iter(), txtbuf.get_end_iter())
        for tagtuple in taglist:
            (sidx, length, tag) = tagtuple
            sitr = txtbuf.get_iter_at_offset(sidx)
            eitr = txtbuf.get_iter_at_offset(sidx+length)
            txtbuf.apply_tag(tag, sitr, eitr)
    
    def activate_result(self, itr):
        if not self.results: return True
        if len(self.results) <= itr.get_line():
            return True
        result = self.results[itr.get_line()]
        
        for tag in itr.get_tags(): #FIXME: Create a findTagByType function?
            if tag.get_property('name') == 'link':
                (itr, itr_end) = self.get_tag_pos(itr, tag)
                filename = self.getTextBuffer().get_text(itr, itr_end, False)
                filename = os.path.join(self.results.search_path, filename)
                filename = Path.full(filename)
                
                cmdList = []
                for itm in self.app.prefs.get('editor').split(' '):
                    if '$1' in itm:
                        itm = itm.replace('$1', filename)
                    if '$n' in itm:
                        itm = itm.replace('$n', result.linenum)
                    cmdList.append(itm)
                subprocess.Popen(cmdList)
                return True
        return False
    
    # Locate start/end of tag at given iterator
    def get_tag_pos(self, itr, tag):
        itr_end = itr.copy()

        # Find start of tag
        while (not itr.begins_tag(tag)):
            itr.backward_char()

        # Find end of tag
        while (not itr_end.ends_tag(tag)):
            itr_end.forward_char()

        return (itr, itr_end)

