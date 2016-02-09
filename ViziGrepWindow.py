import subprocess, re, os, traceback
from threading import Thread
from gi.repository import Gtk, Gdk, GObject
from Window import Window
from GrepEngine import GrepEngine, GrepResult, GrepResults, NoResultsException, BadPathException, BadRegexException
from PreferencesWindow import PreferencesWindow
from Path import Path

class ViziGrepWindow(Window):
    gtk_builder_file   = "vizigrep.glade"
    window_name        = "win_main"

    def __init__(self, prefs):
        self.results = []
        Window.__init__(self, self.gtk_builder_file, self.window_name)
        self.prefs = prefs
        self.ge = GrepEngine()
        self.ge.exclude_dirs = self.prefs.get('exclude-dirs')
        self.ge.exclude_files = self.prefs.get('exclude-files')

        txtbuf = self.txt_results.get_buffer()
        self.tag_fixed = txtbuf.create_tag("fixed", family="Monospace")
        self.tag_link = txtbuf.create_tag("link", foreground="Blue")
        self.tag_red = txtbuf.create_tag("color", foreground="Red")
        self.tag_green = txtbuf.create_tag("green", foreground="Dark Green")
        
        self.gtk_window.connect('delete_event', self.close)
        self.btn_search.connect('clicked', self.btn_search_clicked)
        self.txt_results.connect('button-press-event', self.results_clicked)
        self.lbl_path.connect('activate-link', self.lbl_path_clicked)
        self.txt_results.connect('motion-notify-event', self.results_mouse_motion)
        self.txt_results.connect('key-press-event', self.results_keypress)
        self.lbl_options.connect('activate-link', self.options_clicked)
        
        (win_width, win_height) = self.prefs.get('window-size')
        self.win_main.resize(win_width,win_height)
        
        self.cbox_path.forall(self.cbox_disable_togglebutton_focus, None)
        self.cbox_search.forall(self.cbox_disable_togglebutton_focus, None)
        
        self.deactivate_on_search = [self.btn_search, self.lbl_path, self.lbl_options, 
                                    self.cbox_search, self.cbox_path, self.txt_results]

    # GtkComboBoxes have an internal GtkToggleButton widget that accepts focus. This is 
    # quite annoying to a user trying to navigate via keyboard so we disable it's focus.
    def cbox_disable_togglebutton_focus(self, widget, data):
        if isinstance(widget,Gtk.ToggleButton):
            widget.set_can_focus(False)

    def activate(self):
        self.reload_search_box()
        self.reload_path_box()
        self.clear_results()
        self.chk_case.set_active(self.prefs.get('case-sensitive'))
        self.cbox_search.get_child().grab_focus()
        self.gtk_window.show_all()
    
    def close(self, win, event):
        self.prefs.set('window-size', self.win_main.get_size())
        self.prefs.set('case-sensitive', self.chk_case.get_active())
        self.prefs.write_prefs()
        Gtk.main_quit()
    
    def lbl_path_clicked(self, lbl):
        btns = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog = Gtk.FileChooserDialog('Choose a folder', self.win_main, Gtk.FileChooserAction.SELECT_FOLDER, btns)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            pathStr = self.trunc_path(dialog.get_filename())
            self.cbox_path.get_child().set_text(Path(pathStr).pretty())
        
        dialog.destroy()
        return True
         
    def trunc_path(self, path):
        if (path.startswith(os.path.expanduser('~'))):
            path = path.replace(os.path.expanduser('~'), '~')
        return path

    def btn_search_clicked(self, data):
        self.clear_results()
        txtbuf = self.txt_results.get_buffer()
        string = self.cbox_search.get_active_text()
        
        path = self.trunc_path(self.cbox_path.get_active_text())
        self.cbox_path.get_child().set_text(path)
        self.last_search_path = path
        
        if not string.strip():
            txtbuf.set_text("You forgot to provide a search string")
            self.cbox_search.get_child().grab_focus()
            return True
        if not path.strip():
            txtbuf.set_text("You forgot to provide a search folder")
            self.cbox_path.get_child().grab_focus()
            return True
        
        self.disable_all()
        self.spinner.start()
        new_thread = Thread(target=self.grep_thread, args=(string, path, self.grep_thread_done))
        new_thread.start()

    def grep_thread(self, string, path, donefn):
        try:
            results = self.ge.grep(string, path, self.prefs.get('match-limit'), self.chk_case.get_active())
            ex = None
        except Exception as e:
            results = None
            ex = e
        GObject.idle_add(donefn, string, path, results, ex)
        
    def grep_thread_done(self, string, path, results, exception):
        if results:
            try:
                self.set_results(results, string)
            except Exception as e:
                print type(e)
                print traceback.format_exc()
            self.add_path_history(path)
            self.add_search_history(string)
        else:
            txtbuf = self.txt_results.get_buffer()
            if isinstance(exception, BadPathException):
                txtbuf.set_text("The given folder does not exist: %s" % path)
            elif isinstance(exception, NoResultsException):
                txtbuf.set_text("No results found")
            elif isinstance(exception, BadRegexException):
                txtbuf.set_text("Search string error: %s" % str(exception))
            else:
                txtbuf.set_text("Unexpected Error: " + str(exception))
                print type(exception)
                print traceback.format_exc()
        self.spinner.stop()
        self.enable_all()

    def disable_all(self):
        for widget in self.deactivate_on_search:
            widget.set_sensitive(False)
            
    def enable_all(self):
        for widget in self.deactivate_on_search:
            widget.set_sensitive(True)
            
    def set_results(self, results, string):
        self.results = results
        txtbuf = self.txt_results.get_buffer()
        max_fnlen = results.max_fnlen()
        max_lnlen = results.max_lnlen()
        taglist = []
        rstr = ''
        
        string = self.escape_regex_str(string)
        for r in results:
            taglist.append( (len(rstr), len(r.fn), self.tag_link) )
            rstr += r.fn
            if max_fnlen > len(r.fn):
                rstr += ' '*(max_fnlen-len(r.fn))
            rstr += ':'
        
            if (self.prefs.get('show-line-numbers')):
                taglist.append( (len(rstr), len(r.linenum), self.tag_green) )
                rstr += r.linenum
                if max_lnlen > len(r.linenum):
                    rstr += " "*(max_lnlen-len(r.linenum))
                rstr += ':'
                
            if self.chk_case.get_active():
                m = re.search(string, r.str)
            else:
                m = re.search(string, r.str, re.IGNORECASE)
            
            if(m and len(m.group()) > 0):
                matched_text = m.group()
                (prematch, match, postmatch) = r.str.partition(matched_text)
                rstr += prematch
                taglist.append( (len(rstr), len(matched_text), self.tag_red) )
                rstr += matched_text
                rstr += postmatch + '\n'
            else:
                rstr += r.str + '\n'
            
        self.lbl_matches.set_text(str(len(results)))
        self.lbl_files.set_text(str(results.unique_fns()))
        txtbuf.set_text(rstr)
        self.apply_tags(txtbuf, rstr, taglist)

    def escape_regex_str(self, regex):
        if '\\' in regex: 
            regex = regex.replace('\\', '\\\\')  # Escape \
        return regex
    
    def apply_tags(self, txtbuf, rstr, taglist):
        txtbuf.apply_tag(self.tag_fixed, txtbuf.get_start_iter(), txtbuf.get_end_iter())
        for tagtuple in taglist:
            (sidx, length, tag) = tagtuple
            sitr = txtbuf.get_iter_at_offset(sidx)
            eitr = txtbuf.get_iter_at_offset(sidx+length)
            txtbuf.apply_tag(tag, sitr, eitr)
        
    def clear_results(self):
        self.txt_results.get_buffer().set_text('')
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
            self.txt_results.grab_focus()
        return True

    def results_keypress(self, txtview, event_key):
        if Gdk.keyval_name(event_key.keyval) in ["Return", "KP_Enter"]:
            txtbuf = self.txt_results.get_buffer()
            txt = txtbuf.get_text(txtbuf.get_start_iter(), txtbuf.get_end_iter(), False)
            itr = txtbuf.get_iter_at_mark( txtbuf.get_insert() )
            self.activate_result(itr)
            return True

    def activate_result(self, itr):
        result = self.results[itr.get_line()]
        for tag in itr.get_tags():
            if tag == self.tag_link:
                (itr, itr_end) = self.get_tag_pos(itr, tag)
                filename = self.txt_results.get_buffer().get_text(itr, itr_end, False)
                fullfn = os.path.join(self.last_search_path, filename)
                p = Path(fullfn)
                fullfn = p.fullpath
                
                cmdList = []
                for itm in self.prefs.get('editor').split(' '):
                    if '$1' in itm:
                        itm = itm.replace('$1', fullfn)
                    if '$n' in itm:
                        itm = itm.replace('$n', result.linenum)

                    cmdList.append(itm)
                    print itm
                
                command = self.prefs.get('editor')
                if '$1' in command:
                    command = command.replace('$1', fullfn)
                else: command = command + " " + fullfn
                if '$n' in command:
                    command = command.replace('$n', result.linenum)

                subprocess.Popen(cmdList)
                return True
        return False
        
    def results_mouse_motion(self, txtview, event):
        (cx, cy) = txtview.window_to_buffer_coords(Gtk.TextWindowType.WIDGET, event.x, event.y)
        itr = txtview.get_iter_at_location(cx, cy)

        cursor = Gdk.Cursor(Gdk.CursorType.XTERM)
        for tag in itr.get_tags():
            if tag == self.tag_link:
                cursor = Gdk.Cursor(Gdk.CursorType.HAND2)
                break

        self.txt_results.get_window(Gtk.TextWindowType.TEXT).set_cursor(cursor)
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
        
    def options_clicked(self, lbl):
        PreferencesWindow(self.prefs).activate()
