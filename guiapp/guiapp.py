import os

import multilogger
import preferences
import mbox

class GuiApp:

    def __init__(self, shortName):
        self.shortName = shortName

        self.appHomeDir = os.path.join(os.path.expanduser('~'), '.config', self.shortName)
        self.__checkHomeDir()

        # Components
        self.log = None
        self.prefs = None
        self.mbox = mbox.mbox()

        # Settings
        self.writePrefsOnClose = True

    def __checkHomeDir(self):
        if not os.path.exists(self.appHomeDir):
            os.mkdir(self.appHomeDir)

    def initLogging(self):
        self.logFilePath = os.path.join(self.appHomeDir, self.shortName + '.log')
        self.log = multilogger.MultiLogger()
        self.log.open_logfile(self.logFilePath)

    def initPrefs(self):
        self.prefsFilePath = os.path.join(self.appHomeDir, self.shortName + '.prefs')
        self.prefs = preferences.Preferences(self.prefsFilePath)

    def shutdown(self):
        if self.log:
            self.log.close_logfile()

        if self.prefs and self.writePrefsOnClose:
            self.prefs.write_prefs()
