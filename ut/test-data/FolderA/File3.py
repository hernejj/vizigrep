import subprocess, re, os, traceback
from threading import Thread
from gi.repository import Gtk, Gdk, GObject
from Window import Window
from GrepEngine import GrepEngine, GrepResult, GrepResults, NoResultsException, BadPathException, BadRegexException
from PreferencesWindow import PreferencesWindow

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


