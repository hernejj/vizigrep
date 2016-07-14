#!/usr/bin/python
# Copyright: Jason J. Herne (hernejj@gmail.com)
# License: GPL-v2 (http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject
from vizigrep.guiapp.guiapp import GuiApp
from ViziGrepWindow import ViziGrepWindow
    
def main(args=None):
    app = GuiApp('vizigrep')
    app.initPrefs()
    app.initLogging()
    app.log.stdout = True
    app.mbox.log = app.log # FIXME: Silly to have this here

    GObject.threads_init()
    vgw = ViziGrepWindow(app)
    vgw.activate()
    Gtk.main()

if __name__ == "__main__":
    main()
