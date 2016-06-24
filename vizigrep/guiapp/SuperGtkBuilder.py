from gi.repository import Gtk, GObject, GtkSource

# GtkBuilder that will populate the given object (representing a Window) with
# all of that window's UI elements as found in the GtkBuilder UI file.
class SuperGtkBuilder(Gtk.Builder):

    def __init__(self, window_object, ui_file_path):
        Gtk.Builder.__init__(self)
        GObject.type_register(GtkSource.View)  # Needed to work with GtkSourceView objects
        self.add_from_file(ui_file_path)
        self.populate_window_with_ui_elements(window_object)

    # Create a data-member in window_object to represent each ui element
    # found in the GtkBuilder UI file.
    def populate_window_with_ui_elements(self, window_object):
        for ui_element in self.get_objects():
            if isinstance(ui_element, Gtk.TreeSelection): continue
            setattr(window_object, Gtk.Buildable.get_name(ui_element), ui_element)
