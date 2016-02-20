from gi.repository import Gtk, Gdk

from guiapp.Window import Window
from PreferencesWindow import PreferencesWindow
from VizigrepTab import VizigrepTab
import Path

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
        self.getActiveTab().setTitleText('[New tab]')
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
        link_activated = self.getActiveTab().activate_result(itr)
       
        if not link_activated:
            txtview.grab_focus()
        return True

    def results_keypress(self, txtview, event_key):
        if Gdk.keyval_name(event_key.keyval) in ["Return", "KP_Enter"]:
            txtbuf = txtview.get_buffer()
            itr = txtbuf.get_iter_at_mark( txtbuf.get_insert() )
            self.getActiveTab().activate_result(itr)
            return True
    
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
