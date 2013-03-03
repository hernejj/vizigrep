from gi.repository import Gtk
from SuperGtkBuilder import SuperGtkBuilder

class Window:

    # The Window this object represents.
    gtk_window = None           

    # GtkBuilder object containing GUI elements.
    builder = None

    def __init__(self, gtk_builder_file, window_name):
        self.builder = SuperGtkBuilder(self, gtk_builder_file)
        self.gtk_window = self.builder.get_object(window_name)
