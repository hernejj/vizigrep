from gi.repository import Gtk
from SuperGtkBuilder import SuperGtkBuilder

class Tab:

    # The Window this object represents.
    gtk_window = None

    # GtkBuilder object containing GUI elements.
    builder = None

    def __init__(self, gtkBuilderFile, containerName, gtkNotebook, tabName):
        self.builder = SuperGtkBuilder(self, gtkBuilderFile)
        self.container = self.builder.get_object(containerName)
        self.gtkNotebook = gtkNotebook

        # Remove the container from the window glade forces us to place it in.
        self.parentWindow = self.builder.get_object("win_main")
        self.parentWindow.remove(self.container)

        self.gtkNotebook.append_page(self.container, Gtk.Label(tabName))
