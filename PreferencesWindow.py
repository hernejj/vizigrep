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
        self.txt_editor_default.set_text( self.prefs.defaults['editor'] )
        self.gtk_window.show_all()
    
    def close(self, win=None, event=None):
        self.gtk_window.hide()
        return True

    

