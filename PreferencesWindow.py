import os
from gi.repository import Gtk, Gdk
from Window import Window

class PreferencesWindow(Window):
    gtk_builder_file   = "prefs-window.glade"
    window_name        = "win_prefs"

    def __init__(self, prefs):
        Window.__init__(self, self.gtk_builder_file, self.window_name)
        self.prefs = prefs

        self.gtk_window.connect('delete_event', self.close)
        self.btn_close.connect('clicked', self.close)
        
    def activate(self):
        self.load_editor()
        self.load_linenum()
        self.gtk_window.show_all()
    
    def close(self, win=None, event=None):
        self.save_editor()
        self.save_linenum()
        
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
