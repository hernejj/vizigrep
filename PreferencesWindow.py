from gi.repository import Gtk

from guiapp.Window import Window

class PreferencesWindow(Window):
    gtk_builder_file   = "ui/prefs-window.glade"
    window_name        = "win_prefs"

    def __init__(self, app):
        Window.__init__(self, app, self.gtk_builder_file, self.window_name)
        self.prefs = app.prefs
        
        self.gtk_window.connect('delete_event', self.close)
        self.btn_close.connect('clicked', self.close)
        self.btn_file_add.connect('clicked', self.add_file)
        self.btn_file_remove.connect('clicked', self.remove_file)
        self.btn_dir_add.connect('clicked', self.add_dir)
        self.btn_dir_remove.connect('clicked', self.remove_dir)
        
        self.init_files_list()
        self.init_dirs_list()
        
    def activate(self):
        self.load_editor()
        self.load_linenum()
        self.load_files_list()
        self.load_dirs_list()
        self.load_match_limit()
        self.load_alternate_row_color()
        self.gtk_window.show_all()
    
    def close(self, win=None, event=None):
        self.save_editor()
        self.save_linenum()
        self.save_files_list()
        self.save_dirs_list()
        self.save_match_limit()
        self.save_alternate_row_color()
        self.prefs.write_prefs()
        self.gtk_window.hide()
        return True
                
    def load_editor(self):
        default_editor = self.prefs.defaults['editor']
        editor = self.prefs.get('editor')
        self.txt_editor_default.set_text(default_editor)
        
        if editor == default_editor:
            self.rad_editor_default.set_active(True)
        else:
            self.rad_editor_custom.set_active(True)
            self.txt_editor_custom.set_text(editor)
    
    def save_editor(self):
        use_default_editor = self.rad_editor_default.get_active()
        custom_editor_cmd  = self.txt_editor_custom.get_text().strip()
        
        if self.rad_editor_default.get_active() or len(custom_editor_cmd) == 0:
            self.prefs.reset_to_default('editor')
        else:
            self.prefs.set('editor', custom_editor_cmd)
        
    def load_linenum(self):    
        self.chk_linenum.set_active(self.prefs.get('show-line-numbers'))

    def save_linenum(self):
        self.prefs.set('show-line-numbers', self.chk_linenum.get_active())
    
    def load_alternate_row_color(self):
        self.chk_alternate_row_color.set_active(self.prefs.get('alternate-row-color'))

    def save_alternate_row_color(self):
        self.prefs.set('alternate-row-color', self.chk_alternate_row_color.get_active())
        
    def init_files_list(self):
        column = Gtk.TreeViewColumn("File Name",  Gtk.CellRendererText(), text=0)
        self.tree_files.append_column(column)

    def add_file(self, btn):
        text = self.txt_file.get_text().strip()
        if len(text) == 0: return True
        
        if '"' in text or "'" in text:
            self.app.mbox.error('ERROR: Filename cannot contain quotes')
            self.txt_file.grab_focus()
            return True
        
        if text in self.prefs.get('exclude-files'):
            self.app.mbox.error('%s is already in the list.' % text)
            self.txt_file.grab_focus()
            return True
        
        self.prefs.list_add('exclude-files', text)
        self.load_files_list()
        self.txt_file.set_text('')
        return True
    
    def remove_file(self, btn):
        model, itr = self.tree_files.get_selection().get_selected()
        if (itr == None): return True
        
        text = self.tree_files.get_model().get_value(itr, 0)
        self.prefs.list_remove('exclude-files', text)
        self.load_files_list()
        return True

    def load_files_list(self):
        model = Gtk.ListStore(str)
        self.tree_files.set_model(model)
        self.prefs.list_sort('exclude-files')
        for fn in self.prefs.get('exclude-files'):
            model.append([fn])

    def save_files_list(self):
        lst = []
        for row in self.tree_files.get_model():
            lst.append(row[0])
        self.prefs.set('exclude-files', lst)
        
    def init_dirs_list(self):
        column = Gtk.TreeViewColumn("Folder Name",  Gtk.CellRendererText(), text=0)
        self.tree_dirs.append_column(column)
    
    def add_dir(self, btn):
        text = self.txt_dir.get_text().strip()
        if len(text) == 0: return True
        
        if '"' in text or "'" in text:
            self.app.mbox.error('Folder name cannot contain quotes')
            self.txt_dir.grab_focus()
            return True
            
        if text in self.prefs.get('exclude-dirs'):
            self.app.mbox.error('%s is already in the list.' % text)
            self.txt_dir.grab_focus()
            return True
        
        self.prefs.list_add('exclude-dirs', text)
        self.load_dirs_list()
        self.txt_dir.set_text('')
        return True
    
    def remove_dir(self, btn):
        model, itr = self.tree_dirs.get_selection().get_selected()
        if (itr == None): return True
        
        text = self.tree_dirs.get_model().get_value(itr, 0)
        self.prefs.list_remove('exclude-dirs', text)
        self.load_dirs_list()
        return True


    def load_dirs_list(self):
        model = Gtk.ListStore(str)
        self.tree_dirs.set_model(model)
        self.prefs.list_sort('exclude-dirs')
        for fn in self.prefs.get('exclude-dirs'):
            model.append([fn])
            
    def save_dirs_list(self):
        lst = []
        for row in self.tree_dirs.get_model():
            lst.append(row[0])
        self.prefs.set('exclude-dirs', lst)
        
    def load_match_limit(self):
        match_limit = self.prefs.get('match-limit')
        
        if match_limit == 0:
            self.chk_matchlimit.set_active(False)
            self.txt_matchlimit.set_text('')
        else:    
            self.chk_matchlimit.set_active(True)
            self.txt_matchlimit.set_text(str(match_limit))
    
    def save_match_limit(self):
        match_limit = self.txt_matchlimit.get_text()
        if not match_limit.isdigit(): return
        mint = int(match_limit)
        
        if self.chk_matchlimit.get_active():
            if mint <= 0: mint = self.prefs.defaults['match-limit']
            self.prefs.set('match-limit', mint)
        else:
            self.prefs.set('match-limit', 0)
        
        
