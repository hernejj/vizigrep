from gi.repository import GObject
from SuperGtkBuilder import SuperGtkBuilder

class Window:

    # The Window this object represents.
    gtk_window = None           

    # GtkBuilder object containing GUI elements.
    builder = None

    def __init__(self, app, gtk_builder_file, window_name, rememberSizePos=False):
        self.app = app
        self.builder = SuperGtkBuilder(self, gtk_builder_file)
        self.gtk_window = self.builder.get_object(window_name)
        self.window_name = window_name
        self.deactivateCallback = None
        self.rememberSizePos = rememberSizePos
        if rememberSizePos:
            self.loadSizePosition()
        
    # Subclasses can override this
    def activate(self):
        self.gtk_window.show_all()
    
    def deactivate(self):
        if self.rememberSizePos:
            self.saveSizePosition()
        
        self.gtk_window.hide()
        if self.deactivateCallback:
            GObject.idle_add(self.deactivateCallback)
    
    # Set function to be called when this window has been deactivated.
    # Caller can set this to get alerted when the user has finished with this
    # window.
    def setDeactivateCallback(self, fn):
        self.deactivateCallback = fn
    
    # save/load uiSizings
    def saveSizePosition(self):
        sizePrefName = self.window_name + '-window-size'
        positionPrefName = self.window_name + '-window-position'
        self.app.prefs.set(sizePrefName, self.gtk_window.get_size())
        self.app.prefs.set(positionPrefName, self.gtk_window.get_position())
        
    def loadSizePosition(self):
        sizePrefName = self.window_name + '-window-size'
        positionPrefName = self.window_name + '-window-position'
        
        size = self.app.prefs.get(sizePrefName)
        if size:
            (width, height) = size
            self.gtk_window.resize(width, height)

        pos = self.app.prefs.get(positionPrefName)
        if pos:
            (x, y) = pos
            self.gtk_window.move(x, y)
