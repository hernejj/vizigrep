import subprocess, re, os, traceback
from threading import Thread
from gi.repository import Gtk, Gdk, GObject

from guiapp.Window import Window

from GrepEngine import GrepEngine, NoResultsException, GrepException, BadRegexException
from PreferencesWindow import PreferencesWindow
import Path

class TextTag:
    def __init_(self, startIdx, length, gtkTag):
        self.startIdx = startIdx
        self.length = length
        self.gtkTag = gtkTag

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

class ViziGrepWindow(Window):
    gtk_builder_file   = "ui/vizigrep.glade"
    window_name        = "win_main"

    def __init__(self, app):
        Window.__init__(self, app, self.gtk_builder_file, self.window_name, True)
        self.app = app
        self.prefs = app.prefs

        self.gtk_window.connect('delete_event', self.close)
        self.gtk_window.connect('key-press-event', self.win_keypress)
        self.notebook.connect('switch-page', self.switched_tab)
        self.btn_search.connect('clicked', self.btn_search_clicked)
        self.lbl_path.connect('activate-link', self.lbl_path_clicked)
        self.lbl_options.connect('activate-link', self.options_clicked)
        self.lbl_new_tab.connect('activate-link', self.new_tab_clicked)
        self.lbl_close_tab.connect('activate-link', self.close_tab_clicked)
         
        self.cbox_path.forall(self.cbox_disable_togglebutton_focus, None)
        self.cbox_search.forall(self.cbox_disable_togglebutton_focus, None)
        
        self.initNotebook()
        self.initNewTab()

    # GtkComboBoxes have an internal GtkToggleButton widget that accepts focus. This is 
    # quite annoying to a user trying to navigate via keyboard so we disable it's focus.
    def cbox_disable_togglebutton_focus(self, widget, data):
        if isinstance(widget,Gtk.ToggleButton):
            widget.set_can_focus(False)

    def activate(self):
        self.reload_search_box()
        self.reload_path_box()
        self.chk_case.set_active(self.prefs.get('case-sensitive'))
        self.cbox_search.get_child().grab_focus()
        self.gtk_window.show_all()
    
    def close(self, win, event):
        self.deactivate()
        self.prefs.set('case-sensitive', self.chk_case.get_active())
        self.prefs.write_prefs()
        Gtk.main_quit()
    
    # Returns 1 if the 1-key constant is given as input (Gdk.KEY_1, Gdk.KEY_2, etc).
    # Returns 10 for Gdk.KEY_0.
    # Returns None if constant given is not recognized as being a Gdk number key constant
    def __GdkNumKey2Int(self, gdkKeyConst):
        rv = gdkKeyConst - 48
        if (rv < 1) or (rv > 10):
            return None
        return rv
    
    def win_keypress(self, win, kb_event):
        # Control is held
        if kb_event.state & Gdk.ModifierType.CONTROL_MASK:
            if kb_event.keyval == Gdk.KEY_t:
                self.new_tab_clicked()
                return True
            if kb_event.keyval == Gdk.KEY_w:
                self.close_tab_clicked()
                return True
        # Alt is held
        if kb_event.state & Gdk.ModifierType.MOD1_MASK:
            # If a number key was pressed, switch to corresponding tab
            numberPressed = self.__GdkNumKey2Int(kb_event.keyval)
            if numberPressed:
                self.notebook.set_current_page(numberPressed-1)
                return True
        return False
    
    def lbl_path_clicked(self, lbl):
        btns = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog = Gtk.FileChooserDialog('Choose a folder', self.win_main, Gtk.FileChooserAction.SELECT_FOLDER, btns)
        startingPath = Path.full(self.prefs.get('last-opened-folder'))
        dialog.set_current_folder(startingPath)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            pathStr = dialog.get_filename()
            self.prefs.set('last-opened-folder', pathStr)
            self.cbox_path.get_child().set_text(Path.pretty(pathStr))
        
        dialog.destroy()
        return True

    def btn_search_clicked(self, data):
        tab = self.getActiveTab()
        if tab.isSearching:
            self.app.mbox.error('There is already a search happening in this tab.')
            return

        self.clear_results()
   
        string = self.cbox_search.get_active_text()
        
        path = Path.pretty(self.cbox_path.get_active_text())
        self.cbox_path.get_child().set_text(path)
        
        if not string.strip():
            tab.getTextBuffer().set_text("You forgot to provide a search string")
            self.cbox_search.get_child().grab_focus()
            return True
        if not path.strip():
            tab.getTextBuffer().set_text("You forgot to provide a search folder")
            self.cbox_path.get_child().grab_focus()
            return True
        
        self.add_path_history(path)
        self.add_search_history(string)
        
        # Pass excludes to tab's grep engine # FIXME: handle case sensitivity this way as well.
        tab.ge.exclude_dirs = self.app.prefs.get('exclude-dirs')
        tab.ge.exclude_files = self.app.prefs.get('exclude-files')
        
        # Update Tab label widgets
        tab.setTitleText(string + " : " + path)
        tab.setSpinner(True)

        tab.startSearch(string, path, self.chk_case.get_active(), self.set_result_status)

    def set_result_status(self, tab):
        results = tab.results
        if results:
            self.lbl_matches.set_text(str(len(results)))
            self.lbl_files.set_text(str(results.unique_fns()))
        else:
            self.lbl_matches.set_text('')
            self.lbl_files.set_text('')

    def clear_results(self):
        self.getActiveTab().getTextBuffer().set_text('')
        self.lbl_matches.set_text('')
        self.lbl_files.set_text('')
        
        mint = self.prefs.get('match-limit')
        if (mint == 0):
            self.lbl_max.set_text("No Limit")
        else:
            self.lbl_max.set_text(str(mint))
        
    def add_path_history(self, path):
        pathlist = self.prefs.get('path-history')
        pathlist.insert(0, path)
        
        newlist = []
        for item in pathlist:
            if item in newlist: continue
            if len(newlist) >= 10: break
            newlist.append(item)

        self.prefs.set('path-history', newlist)
        self.reload_path_box()
        
    def add_search_history(self, string):
        searchlist = self.prefs.get('search-history')
        searchlist.insert(0, string)
        
        newlist = []
        for item in searchlist:
            if item in newlist: continue
            if len(newlist) >= 10: break
            newlist.append(item)

        self.prefs.set('search-history', newlist)
        self.reload_search_box()
        
    def reload_search_box(self):
        self.cbox_search.get_model().clear()
        
        search_list = self.prefs.get('search-history')
        if len(search_list) > 0:
            self.cbox_search.get_child().set_text(search_list[0])
        for string in search_list:
            self.cbox_search.append_text(string)        
        
    def reload_path_box(self):
        self.cbox_path.get_model().clear()
       
        path_list = self.prefs.get('path-history')
        if len(path_list) > 0:
            self.cbox_path.get_child().set_text(path_list[0])
        for path in path_list:
            self.cbox_path.append_text(path)

    def results_clicked(self, txtview, event_button):
        if (event_button.button != 1): return False
        (cx, cy) = txtview.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, event_button.x, event_button.y)
        itr = txtview.get_iter_at_location(cx, cy)
        link_activated = self.activate_result(itr)
       
        if not link_activated:
            txtview.grab_focus()
        return True

    def results_keypress(self, txtview, event_key):
        if Gdk.keyval_name(event_key.keyval) in ["Return", "KP_Enter"]:
            txtbuf = txtview.get_buffer()
            itr = txtbuf.get_iter_at_mark( txtbuf.get_insert() )
            self.activate_result(itr)
            return True
    
    # FIXME: Should this belong to VizigepTab?
    def activate_result(self, itr):
        tab = self.getActiveTab()
        if not tab.results: return True

        if len(tab.results) <= itr.get_line():
            return True
        result = tab.results[itr.get_line()]
        
        for tag in itr.get_tags():
            if tag.get_property('name') == 'link':
                (itr, itr_end) = self.get_tag_pos(itr, tag)
                filename = tab.getTextBuffer().get_text(itr, itr_end, False)
                filename = os.path.join(tab.results.search_path, filename)
                filename= Path.full(filename)
                
                cmdList = []
                for itm in self.prefs.get('editor').split(' '):
                    if '$1' in itm:
                        itm = itm.replace('$1', filename)
                    if '$n' in itm:
                        itm = itm.replace('$n', result.linenum)

                    cmdList.append(itm)
                    print itm

                subprocess.Popen(cmdList)
                return True
        return False
        
    def results_mouse_motion(self, txtview, event):
        (cx, cy) = txtview.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, event.x, event.y)
        itr = txtview.get_iter_at_location(cx, cy)

        cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
        for tag in itr.get_tags():
            if tag.get_property('name') == 'link':
                cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
                break

        txtview.get_window(Gtk.TextWindowType.TEXT).set_cursor(cursor)
        return False

    # FIXME: Should this belong to VizigepTab?
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
        
    def options_clicked(self, lbl):
        PreferencesWindow(self.app).activate()
        return True #Prevents attempted activation of link button's URI
    
    def new_tab_clicked(self, lbl=None):
        tabIdx = self.initNewTab()
        self.notebook.show_all()
        self.notebook.set_current_page(tabIdx)
        return True #Prevents attempted activation of link button's URI
    
    def close_tab_clicked(self, lbl=None):
        tab = self.getActiveTab()
        if tab.isSearching:
            tab.ge.cancel()
        self.deleteActiveTab()
        return True #Prevents attempted activation of link button's URI
    
    def switched_tab(self, notebook, junkPagePtr, pageIdx):
        tab = notebook.get_nth_page(pageIdx)
        self.set_result_status(tab)
    
    def initNotebook(self):
        # Notebooks contain 3 built-in tabs by default. Remove all of them.
        while self.notebook.get_n_pages() > 0:
            self.notebook.remove_page(-1)
        
    def initNewTab(self):
        newTab = VizigrepTab(self.app, self.notebook)
        
        # Connect Signal handlers
        txtview = newTab.getTextView()
        txtview.connect('button-press-event', self.results_clicked)
        txtview.connect('motion-notify-event', self.results_mouse_motion)
        txtview.connect('key-press-event', self.results_keypress)
        return newTab.getIndex()
        
    def deleteActiveTab(self):
        if self.notebook.get_n_pages() == 1:
            self.clear_results()
        else:
            self.notebook.remove_page(self.notebook.get_current_page())
        
    def getActiveTab(self):
        tabIdx = self.notebook.get_current_page()
        return self.notebook.get_nth_page(tabIdx)
